import React, { useEffect, useState } from 'react';
import { Progress, Text, Paper, Group, Badge } from '@mantine/core';
import { IconCheck, IconX } from '@tabler/icons-react';

interface TaskProgressProps {
    taskId: string;
    onComplete?: (success: boolean) => void;
}

interface TaskStatus {
    progress: number;
    status: 'running' | 'completed' | 'failed';
    message: string;
    source?: string;
}

export const TaskProgress: React.FC<TaskProgressProps> = ({ taskId, onComplete }) => {
    const [taskStatus, setTaskStatus] = useState<TaskStatus>({
        progress: 0,
        status: 'running',
        message: 'Iniciando tarea...'
    });

    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8000/ws/task/${taskId}`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setTaskStatus(data);

            if (data.status === 'completed' || data.status === 'failed') {
                onComplete?.(data.status === 'completed');
                ws.close();
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setTaskStatus(prev => ({
                ...prev,
                status: 'failed',
                message: 'Error de conexión'
            }));
        };

        return () => {
            ws.close();
        };
    }, [taskId, onComplete]);

    const getStatusColor = () => {
        switch (taskStatus.status) {
            case 'completed':
                return 'green';
            case 'failed':
                return 'red';
            default:
                return 'blue';
        }
    };

    const getStatusIcon = () => {
        switch (taskStatus.status) {
            case 'completed':
                return <IconCheck size={16} />;
            case 'failed':
                return <IconX size={16} />;
            default:
                return null;
        }
    };

    return (
        <Paper shadow="sm" p="md" withBorder>
            <Group position="apart" mb="xs">
                <Text size="sm" weight={500}>
                    {taskStatus.source || 'Tarea en progreso'}
                </Text>
                <Badge 
                    color={getStatusColor()} 
                    variant="light"
                    leftSection={getStatusIcon()}
                >
                    {taskStatus.status === 'running' ? 'En progreso' : 
                     taskStatus.status === 'completed' ? 'Completado' : 'Error'}
                </Badge>
            </Group>
            
            <Progress 
                value={taskStatus.progress} 
                color={getStatusColor()} 
                size="xl" 
                radius="xl" 
                striped 
                animate={taskStatus.status === 'running'}
                mb="sm"
            />
            
            <Text size="sm" color="dimmed">
                {taskStatus.message}
            </Text>
        </Paper>
    );
};

export default TaskProgress;
