// tbot/frontend/src/components/Layout.tsx
import { AppShell, Burger, Group, NavLink } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Outlet, Link } from 'react-router-dom';
import { IconChartArcs, IconAdjustments } from '@tabler/icons-react';

export default function Layout() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          TBot Dashboard
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <NavLink
          label="Dashboard"
          component={Link}
          to="/"
          leftSection={<IconChartArcs size="1rem" stroke={1.5} />}
        />
        <NavLink
          label="Strategy Management"
          component={Link}
          to="/strategies"
          leftSection={<IconAdjustments size="1rem" stroke={1.5} />}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
