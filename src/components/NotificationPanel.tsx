import React, { useState, useEffect } from 'react';
import { Card, Text, Stack, Group, Badge, ActionIcon, ScrollArea } from '@mantine/core';
import { IconBell, IconCheck, IconX } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
  timestamp: string;
  read: boolean;
}

export const NotificationPanel: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // Configurar WebSocket para notificaciones en tiempo real
    const ws = new WebSocket(
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/notifications`
    );

    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      addNotification(notification);
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    // Actualizar contador de no leídos
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev]);

    // Mostrar notificación toast
    notifications.show({
      title: notification.type.charAt(0).toUpperCase() + notification.type.slice(1),
      message: notification.message,
      color: getNotificationColor(notification.type),
      icon: getNotificationIcon(notification.type),
    });
  };

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n =>
        n.id === id ? { ...n, read: true } : n
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'green';
      case 'error':
        return 'red';
      case 'warning':
        return 'yellow';
      default:
        return 'blue';
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <IconCheck size={16} />;
      case 'error':
        return <IconX size={16} />;
      default:
        return <IconBell size={16} />;
    }
  };

  return (
    <Card shadow="sm" p="lg" radius="md" withBorder>
      <Group position="apart" mb="md">
        <Group>
          <IconBell size={24} />
          <Text weight={500}>Notificaciones</Text>
          {unreadCount > 0 && (
            <Badge color="red" variant="filled" size="sm">
              {unreadCount}
            </Badge>
          )}
        </Group>
        {unreadCount > 0 && (
          <ActionIcon onClick={markAllAsRead} variant="subtle">
            <IconCheck size={16} />
          </ActionIcon>
        )}
      </Group>

      <ScrollArea h={400}>
        <Stack spacing="xs">
          {notifications.map((notification) => (
            <Card
              key={notification.id}
              p="sm"
              radius="sm"
              withBorder
              style={{
                opacity: notification.read ? 0.7 : 1,
                cursor: 'pointer',
              }}
              onClick={() => markAsRead(notification.id)}
            >
              <Group position="apart">
                <Group>
                  {getNotificationIcon(notification.type)}
                  <Text size="sm">{notification.message}</Text>
                </Group>
                <Badge
                  color={getNotificationColor(notification.type)}
                  variant="light"
                  size="sm"
                >
                  {notification.type}
                </Badge>
              </Group>
              <Text size="xs" color="dimmed" mt="xs">
                {new Date(notification.timestamp).toLocaleString()}
              </Text>
            </Card>
          ))}
        </Stack>
      </ScrollArea>
    </Card>
  );
};

export default NotificationPanel;
