import React from 'react';
import {
  Card,
  Text,
  Group,
  Badge,
  Stack,
  ActionIcon,
  ScrollArea,
  Tooltip,
  Grid,
  Paper,
} from '@mantine/core';
import {
  IconDownload,
  IconExternalLink,
  IconShare,
  IconBookmark,
  IconCalendar,
  IconBuilding,
  IconCoin,
  IconFileText,
} from '@tabler/icons-react';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  entity: string;
  date: string;
  amount: number;
  status: string;
  documentUrl: string;
  tags: string[];
}

interface SearchResultsProps {
  results: SearchResult[];
  onDownload: (id: string) => void;
  onShare: (id: string) => void;
  onBookmark: (id: string) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  onDownload,
  onShare,
  onBookmark,
}) => {
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'activo':
        return 'green';
      case 'cerrado':
        return 'red';
      case 'pendiente':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  return (
    <Card shadow="sm" p="lg" radius="md" withBorder>
      <ScrollArea h={600}>
        <Stack spacing="md">
          {results.map((result) => (
            <Paper key={result.id} p="md" withBorder>
              <Grid>
                <Grid.Col span={9}>
                  <Group position="apart">
                    <Text weight={500} size="lg">
                      {result.title}
                    </Text>
                    <Badge color={getStatusColor(result.status)}>
                      {result.status}
                    </Badge>
                  </Group>

                  <Text size="sm" color="dimmed" mt="xs">
                    {result.description}
                  </Text>

                  <Group spacing="xs" mt="md">
                    <Group spacing={4}>
                      <IconBuilding size={16} />
                      <Text size="sm">{result.entity}</Text>
                    </Group>
                    <Group spacing={4}>
                      <IconCalendar size={16} />
                      <Text size="sm">
                        {new Date(result.date).toLocaleDateString()}
                      </Text>
                    </Group>
                    <Group spacing={4}>
                      <IconCoin size={16} />
                      <Text size="sm">{formatAmount(result.amount)}</Text>
                    </Group>
                  </Group>

                  <Group spacing={5} mt="sm">
                    {result.tags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="outline"
                        size="sm"
                        style={{ textTransform: 'none' }}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </Group>
                </Grid.Col>

                <Grid.Col span={3}>
                  <Stack align="flex-end" justify="space-between" h="100%">
                    <Group>
                      <Tooltip label="Descargar">
                        <ActionIcon
                          variant="light"
                          color="blue"
                          onClick={() => onDownload(result.id)}
                        >
                          <IconDownload size={18} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Compartir">
                        <ActionIcon
                          variant="light"
                          color="grape"
                          onClick={() => onShare(result.id)}
                        >
                          <IconShare size={18} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Guardar">
                        <ActionIcon
                          variant="light"
                          color="orange"
                          onClick={() => onBookmark(result.id)}
                        >
                          <IconBookmark size={18} />
                        </ActionIcon>
                      </Tooltip>
                    </Group>

                    <Tooltip label="Ver documento">
                      <ActionIcon
                        variant="filled"
                        color="blue"
                        size="lg"
                        component="a"
                        href={result.documentUrl}
                        target="_blank"
                      >
                        <IconFileText size={20} />
                      </ActionIcon>
                    </Tooltip>
                  </Stack>
                </Grid.Col>
              </Grid>
            </Paper>
          ))}
        </Stack>
      </ScrollArea>
    </Card>
  );
};

export default SearchResults;
