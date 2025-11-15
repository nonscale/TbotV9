// tbot/frontend/src/pages/StrategyManagementPage.tsx
import { useState, useEffect } from 'react';
import { Title, Table, Button, Group, ActionIcon, Modal, TextInput, Textarea, Switch, Stack, Divider } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { IconPencil, IconTrash } from '@tabler/icons-react';
import apiClient from '../services/api';
import RuleNode from '../components/RuleNode';

// --- Type definitions ---
interface ConditionNode { type: 'condition'; value: string; timeframe?: string; }
interface GroupNode { type: 'group'; operator: 'AND' | 'OR'; children: Node[]; }
type Node = ConditionNode | GroupNode;
interface ScanRules { first_scan?: GroupNode; second_scan?: GroupNode; }
interface Strategy {
  id: number;
  name: string;
  description: string;
  broker: string;
  market: string;
  scan_rules: ScanRules;
  is_active: boolean;
  cron_schedule?: string;
}

interface StrategyFormValues {
    name: string;
    description: string;
    broker: string;
    market: string;
    is_active: boolean;
    cron_schedule: string;
    first_scan: GroupNode;
    second_scan: GroupNode;
}

const EMPTY_GROUP: GroupNode = { type: 'group', operator: 'AND', children: [] };
const EMPTY_STRATEGY_FORM: StrategyFormValues = {
    name: '',
    description: '',
    broker: 'upbit',
    market: 'KRW-BTC',
    is_active: false,
    cron_schedule: '*/5 * * * *',
    first_scan: { type: 'group', operator: 'AND', children: [{ type: 'condition', value: 'amount > 100000000' }] },
    second_scan: { type: 'group', operator: 'AND', children: [] },
};

export default function StrategyManagementPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);

  const form = useForm<StrategyFormValues>({ initialValues: EMPTY_STRATEGY_FORM });

  const fetchStrategies = async () => {
    try {
      const response = await apiClient.get<Strategy[]>('/strategies/');
      setStrategies(response.data);
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const handleEditOpen = (strategy: Strategy) => {
    setEditingStrategy(strategy);
    form.setValues({
      name: strategy.name,
      description: strategy.description || '',
      broker: strategy.broker,
      market: strategy.market,
      is_active: strategy.is_active,
      cron_schedule: strategy.cron_schedule || '',
      first_scan: strategy.scan_rules.first_scan || EMPTY_GROUP,
      second_scan: strategy.scan_rules.second_scan || EMPTY_GROUP,
    });
    openModal();
  };

  const handleAddOpen = () => { setEditingStrategy(null); form.reset(); openModal(); };

  const handleSubmit = async (values: StrategyFormValues) => {
    const payload = { ...values, scan_rules: { first_scan: values.first_scan, second_scan: values.second_scan } };
    try {
      if (editingStrategy) {
        await apiClient.put(`/strategies/${editingStrategy.id}`, payload);
      } else {
        await apiClient.post('/strategies/', payload);
      }
      fetchStrategies(); closeModal();
    } catch (error) { console.error('Failed to save strategy:', error); }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
        try {
            await apiClient.delete(`/strategies/${id}`);
            fetchStrategies();
        } catch (error) {
            console.error('Failed to delete strategy:', error);
        }
    }
  };

  const handleStartScan = async (id: number) => {
    try {
      await apiClient.post(`/scans/${id}/run`);
      alert('Manual scan started successfully!');
    } catch (error) {
      console.error('Failed to start scan:', error);
    }
  };

  const handleStopScan = async (id: number) => {
    try {
      await apiClient.post(`/scans/${id}/stop`);
      alert('Manual scan stopped successfully!');
    } catch (error) {
      console.error('Failed to stop scan:', error);
    }
  };

  const rows = strategies.map((strategy) => (
    <Table.Tr key={strategy.id}>
      <Table.Td>{strategy.name}</Table.Td>
      <Table.Td>{strategy.cron_schedule || 'Manual'}</Table.Td>
      <Table.Td><Switch checked={strategy.is_active} readOnly label={strategy.is_active ? "Scheduled" : "Inactive"} /></Table.Td>
      <Table.Td>
        <Group>
          <Button size="xs" onClick={() => handleStartScan(strategy.id)}>Run Once</Button>
          <Button size="xs" color="orange" onClick={() => handleStopScan(strategy.id)}>Stop All</Button>
          <ActionIcon variant="outline" onClick={() => handleEditOpen(strategy)}><IconPencil size={16} /></ActionIcon>
          <ActionIcon variant="outline" color="red" onClick={() => handleDelete(strategy.id)}><IconTrash size={16} /></ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <>
      <Modal opened={modalOpened} onClose={closeModal} title={editingStrategy ? 'Edit Strategy' : 'Add New Strategy'} size="xl">
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <TextInput label="Name" required {...form.getInputProps('name')} />
            <Textarea label="Description" {...form.getInputProps('description')} />
            <Group grow>
              <TextInput label="Broker" required {...form.getInputProps('broker')} />
              <TextInput label="Market" required {...form.getInputProps('market')} />
            </Group>

            <Divider my="sm" label={<Title order={4}>1st Scan Rules (Real-time Data)</Title>} />
            <RuleNode path="first_scan" form={form} />

            <Divider my="sm" label={<Title order={4}>2nd Scan Rules (Historical Data)</Title>} />
            <RuleNode path="second_scan" form={form} />

            <TextInput label="Cron Schedule" placeholder="*/5 * * * *" {...form.getInputProps('cron_schedule')} mt="md" />
            <Switch label="Activate Schedule" {...form.getInputProps('is_active', { type: 'checkbox' })} />
            <Button type="submit" mt="md">Save</Button>
          </Stack>
        </form>
      </Modal>

      <Group justify="space-between" mb="md">
        <Title order={1}>Strategy Management</Title>
        <Button onClick={handleAddOpen}>Add New Strategy</Button>
      </Group>

      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Schedule</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
