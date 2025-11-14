// tbot/frontend/src/pages/StrategyManagementPage.tsx
import { useState, useEffect } from 'react';
import { Title, Table, Button, Group, ActionIcon, Modal, TextInput, Textarea, Switch, JsonInput, Stack } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { IconPencil, IconTrash } from '@tabler/icons-react';
import apiClient from '../services/api';

interface Strategy {
  id: number;
  name: string;
  description: string;
  broker: string;
  market: string;
  scan_rules: {
    first_scan?: string;
    second_scan?: object;
  };
  is_active: boolean;
  cron_schedule?: string;
}

const EMPTY_STRATEGY_FORM = {
    name: '',
    description: '',
    broker: 'upbit',
    market: 'KRW-BTC',
    first_scan: 'amount > 100000000',
    second_scan: {},
    is_active: false,
    cron_schedule: '*/5 * * * *', // Default to every 5 minutes
};

export default function StrategyManagementPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);

  const form = useForm({
    initialValues: EMPTY_STRATEGY_FORM,
  });

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
        ...strategy,
        first_scan: strategy.scan_rules?.first_scan || '',
        second_scan: strategy.scan_rules?.second_scan || {},
        cron_schedule: strategy.cron_schedule || '',
    });
    openModal();
  };

  const handleAddOpen = () => {
    setEditingStrategy(null);
    form.setValues(EMPTY_STRATEGY_FORM);
    openModal();
  };

  const handleSubmit = async (values: typeof form.values) => {
    const payload = {
        name: values.name,
        description: values.description,
        broker: values.broker,
        market: values.market,
        is_active: values.is_active,
        cron_schedule: values.cron_schedule,
        scan_rules: {
            first_scan: values.first_scan,
            second_scan: values.second_scan,
        }
    };
    try {
      if (editingStrategy) {
        await apiClient.put(`/strategies/${editingStrategy.id}`, payload);
      } else {
        await apiClient.post('/strategies/', payload);
      }
      fetchStrategies();
      closeModal();
    } catch (error) {
      console.error('Failed to save strategy:', error);
    }
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

  // Manual scan buttons remain for immediate testing
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
      <Table.Td>{strategy.scan_rules?.first_scan || 'N/A'}</Table.Td>
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
      <Modal opened={modalOpened} onClose={closeModal} title={editingStrategy ? 'Edit Strategy' : 'Add New Strategy'} size="lg">
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <TextInput label="Name" required {...form.getInputProps('name')} />
            <Textarea label="Description" {...form.getInputProps('description')} />
            <Group grow>
                <TextInput label="Broker" required {...form.getInputProps('broker')} />
                <TextInput label="Market" required {...form.getInputProps('market')} />
            </Group>
            <Textarea label="1st Scan Rule (Pandas Query)" required autosize minRows={2} {...form.getInputProps('first_scan')} />
            <JsonInput label="2nd Scan Rules (JSON)" formatOnBlur autosize minRows={4} {...form.getInputProps('second_scan')} />
            <TextInput label="Cron Schedule" placeholder="*/5 * * * *" {...form.getInputProps('cron_schedule')} />
            <Switch label="Activate Schedule" {...form.getInputProps('is_active', { type: 'checkbox' })} />
            <Button type="submit">Save</Button>
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
            <Table.Th>1st Scan Rule</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
