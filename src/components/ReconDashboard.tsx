import React, { useState } from 'react';
import {
  AppShell,
  Navbar,
  Header,
  Grid,
  Container,
  Title,
  Group,
  Button,
  TextInput,
  Select,
} from '@mantine/core';
import { IconSearch, IconFilter } from '@tabler/icons-react';
import TaskProgress from './TaskProgress';
import NotificationPanel from './NotificationPanel';
import SearchResults from './SearchResults';

export const ReconDashboard: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [filterEntity, setFilterEntity] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');

  const handleSearch = async () => {
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          filters: {
            entity: filterEntity,
            status: filterStatus,
          },
        }),
      });

      const data = await response.json();
      setSearchResults(data.results);
      setCurrentTaskId(data.taskId);
    } catch (error) {
      console.error('Error al realizar la búsqueda:', error);
    }
  };

  const handleDownload = async (id: string) => {
    // Implementar lógica de descarga
  };

  const handleShare = async (id: string) => {
    // Implementar lógica de compartir
  };

  const handleBookmark = async (id: string) => {
    // Implementar lógica de guardado
  };

  return (
    <AppShell
      padding="md"
      navbar={
        <Navbar width={{ base: 300 }} p="xs">
          <NotificationPanel />
        </Navbar>
      }
      header={
        <Header height={60} p="xs">
          <Container>
            <Group position="apart">
              <Title order={3}>Licitómetro RECON</Title>
            </Group>
          </Container>
        </Header>
      }
    >
      <Container size="xl">
        <Grid>
          <Grid.Col span={12}>
            <Group position="apart">
              <Group>
                <TextInput
                  icon={<IconSearch size={14} />}
                  placeholder="Buscar licitaciones..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.currentTarget.value)}
                  style={{ width: 400 }}
                />
                <Select
                  placeholder="Entidad"
                  value={filterEntity}
                  onChange={setFilterEntity}
                  data={[
                    { value: 'minsal', label: 'Ministerio de Salud' },
                    { value: 'mineduc', label: 'Ministerio de Educación' },
                    // Agregar más entidades
                  ]}
                  style={{ width: 200 }}
                />
                <Select
                  placeholder="Estado"
                  value={filterStatus}
                  onChange={setFilterStatus}
                  data={[
                    { value: 'activo', label: 'Activo' },
                    { value: 'cerrado', label: 'Cerrado' },
                    { value: 'pendiente', label: 'Pendiente' },
                  ]}
                  style={{ width: 150 }}
                />
              </Group>
              <Button
                leftIcon={<IconFilter size={14} />}
                onClick={handleSearch}
              >
                Buscar
              </Button>
            </Group>
          </Grid.Col>

          <Grid.Col span={12}>
            {currentTaskId && (
              <TaskProgress
                taskId={currentTaskId}
                onComplete={(success) => {
                  if (success) {
                    // Actualizar resultados si es necesario
                  }
                }}
              />
            )}
          </Grid.Col>

          <Grid.Col span={12}>
            <SearchResults
              results={searchResults}
              onDownload={handleDownload}
              onShare={handleShare}
              onBookmark={handleBookmark}
            />
          </Grid.Col>
        </Grid>
      </Container>
    </AppShell>
  );
};

export default ReconDashboard;
