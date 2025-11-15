// tbot/frontend/src/components/RuleNode.tsx
import { Group, Select, TextInput, ActionIcon, Stack, Paper, Button } from '@mantine/core';
import { IconTrash, IconPlus } from '@tabler/icons-react';
import { UseFormReturnType } from '@mantine/form';

// Define types to match backend Pydantic models
interface ConditionNode {
  type: 'condition';
  value: string;
}

interface GroupNode {
  type: 'group';
  operator: 'AND' | 'OR';
  children: Node[];
}

type Node = ConditionNode | GroupNode;

interface RuleNodeProps {
  path: string; // e.g., "first_scan.children.0.children.1"
  form: UseFormReturnType<any>;
}

export default function RuleNode({ path, form }: RuleNodeProps) {
  const node: Node = form.getInputProps(`${path}`).value;

  const handleAddCondition = () => {
    form.insertListItem(`${path}.children`, { type: 'condition', value: '' });
  };

  const handleAddGroup = () => {
    form.insertListItem(`${path}.children`, { type: 'group', operator: 'AND', children: [] });
  };

  const handleRemove = () => {
    const parentPath = path.substring(0, path.lastIndexOf('.'));
    const index = parseInt(path.substring(path.lastIndexOf('.') + 1));
    form.removeListItem(parentPath, index);
  };

  if (node.type === 'condition') {
    return (
      <Group grow>
        <Select
          label="Timeframe"
          placeholder="Select timeframe"
          data={[
            { value: '', label: 'None (1st Scan)' },
            { value: 'day', label: 'Day' },
            { value: 'minute60', label: '60 Minutes' },
            { value: 'minute30', label: '30 Minutes' },
            { value: 'minute10', label: '10 Minutes' },
            { value: 'minute5', label: '5 Minutes' },
          ]}
          {...form.getInputProps(`${path}.timeframe`)}
        />
        <TextInput
          label="Condition"
          placeholder="e.g., close > open"
          style={{ flex: 1 }}
          {...form.getInputProps(`${path}.value`)}
        />
        <ActionIcon color="red" onClick={handleRemove} mt="xl"><IconTrash size={16} /></ActionIcon>
      </Group>
    );
  }

  if (node.type === 'group') {
    return (
      <Paper withBorder p="sm" style={{backgroundColor: 'rgba(0,0,0,0.2)'}}>
        <Stack>
          <Group justify="space-between">
            <Select
              data={['AND', 'OR']}
              {...form.getInputProps(`${path}.operator`)}
            />
            <Group>
              <Button size="xs" variant="outline" onClick={handleAddCondition} leftSection={<IconPlus size={14}/>}>Add Condition</Button>
              <Button size="xs" variant="outline" onClick={handleAddGroup} leftSection={<IconPlus size={14}/>}>Add Group</Button>
              <ActionIcon color="red" onClick={handleRemove}><IconTrash size={16} /></ActionIcon>
            </Group>
          </Group>
          <Stack pl="md">
            {node.children.map((_, index) => (
              <RuleNode key={index} path={`${path}.children.${index}`} form={form} />
            ))}
          </Stack>
        </Stack>
      </Paper>
    );
  }

  return null;
}
