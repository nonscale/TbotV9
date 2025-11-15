// tbot/frontend/src/pages/DashboardPage.tsx
import { useMemo } from 'react';
import { Title, Table, Paper } from '@mantine/core';
import { useWebSocket } from '../hooks/useWebSocket';

interface ScanResult {
  strategy_name: string;
  ticker: string;
  timestamp: string;
  details: {
    price: number;
    volume: number;
    amount: number;
  };
}

const WS_URL = 'ws://localhost:8000/ws/v1/updates?token=fake-token';

export default function DashboardPage() {
  const allMessages = useWebSocket(WS_URL);

  const scanResults = useMemo(() => {
    return allMessages
      .filter(msg => msg.event === 'scan_result_found')
      .map(msg => msg.payload as ScanResult)
      // Sort by timestamp descending to show newest first
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [allMessages]);

  const rows = scanResults.map((result) => (
    <Table.Tr key={`${result.ticker}-${result.timestamp}`}>
      <Table.Td>{new Date(result.timestamp).toLocaleTimeString()}</Table.Td>
      <Table.Td>{result.strategy_name}</Table.Td>
      <Table.Td>{result.ticker}</Table.Td>
      <Table.Td>{result.details.price.toLocaleString()}</Table.Td>
      <Table.Td>{(result.details.amount / 100000000).toFixed(2)}억</Table.Td>
    </Table.Tr>
  ));

  return (
    <>
      <Title order={1} mb="md">Real-time Scan Dashboard</Title>
      <Paper withBorder shadow="sm" p="md">
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Time</Table.Th>
              <Table.Th>Strategy</Table.Th>
              <Table.Th>Ticker</Table.Th>
              <Table.Th>Price</Table.Th>
              <Table.Th>Amount</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {rows.length > 0 ? rows : <Table.Tr><Table.Td colSpan={5}>Waiting for scan results...</Table.Td></Table.Tr>}
          </Table.Tbody>
        </Table>
      </Paper>
    </>
  );
}
