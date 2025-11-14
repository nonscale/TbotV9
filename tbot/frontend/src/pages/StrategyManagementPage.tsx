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
  scan_rules: any;
  is_active: boolean;
}

const EMPTY_STRATEGY: Omit<Strategy, 'id'> = {
    name: '',
    description: '',
    broker: 'upbit',
    market: 'KRW-BTC',
    scan_rules: { min_price: 1000 },
    is_active: false,
};

export default function StrategyManagementPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);

  const form = useForm({
    initialValues: EMPTY_STRATEGY,
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
    form.setValues(strategy);
    openModal();
  };

  const handleAddOpen = () => {
    setEditingStrategy(null);
    form.setValues(EMPTY_STRATEGY);
    openModal();
  };

  const handleSubmit = async (values: typeof form.values) => {
    try {
      if (editingStrategy) {
        await apiClient.put(`/strategies/${editingStrategy.id}`, values);
      } else {
        await apiClient.post('/strategies/', values);
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

  const handleStartScan = async (id: number) => {
    try {
      await apiClient.post(`/scans/${id}/run`);
      alert('Scan started successfully!');
    } catch (error) {
      console.error('Failed to start scan:', error);
    }
  };

  const handleStopScan = async (id: number) => {
    try {
      await apiClient.post(`/scans/${id}/stop`);
      alert('Scan stopped successfully!');
    } catch (error) {
      console.error('Failed to stop scan:', error);
    }
  };

  const rows = strategies.map((strategy) => (
    <Table.Tr key={strategy.id}>
      <Table.Td>{strategy.name}</Table.Td>
      <Table.Td>{strategy.broker}</Table.Td>
      <Table.Td>{strategy.market}</Table.Td>
      <Table.Td><Switch checked={strategy.is_active} readOnly /></Table.Td>
      <Table.Td>
        <Group>
          <Button size="xs" onClick={() => handleStartScan(strategy.id)} disabled={!strategy.is_active}>Start</Button>
          <Button size="xs" color="orange" onClick={() => handleStopScan(strategy.id)}>Stop</Button>
          <ActionIcon variant="outline" onClick={() => handleEditOpen(strategy)}><IconPencil size={16} /></ActionIcon>
          <ActionIcon variant="outline" color="red" onClick={() => handleDelete(strategy.id)}><IconTrash size={16} /></ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <>
      <Modal opened={modalOpened} onClose={closeModal} title={editingStrategy ? 'Edit Strategy' : 'Add New Strategy'}>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <TextInput label="Name" required {...form.getInputProps('name')} />
            <Textarea label="Description" {...form.getInputProps('description')} />
            <TextInput label="Broker" required {...form.getInputProps('broker')} />
            <TextInput label="Market" required {...form.getInputProps('market')} />
            <JsonInput label="Scan Rules" required formatOnBlur autosize minRows={4} {...form.getInputProps('scan_rules')} />
            <Switch label="Active" {...form.getInputProps('is_active', { type: 'checkbox' })} />
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
            <Table.Th>Broker</Table.Th>
            <Table.Th>Market</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
