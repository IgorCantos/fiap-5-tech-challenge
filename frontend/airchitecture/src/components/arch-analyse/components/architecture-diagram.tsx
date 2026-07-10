'use client';

import {
  Box,
  Card,
  CardContent,
  Stack,
  Typography,
} from '@mui/material';
import CloudOutlinedIcon from '@mui/icons-material/CloudOutlined';
import HubOutlinedIcon from '@mui/icons-material/HubOutlined';
import StorageOutlinedIcon from '@mui/icons-material/StorageOutlined';
import SecurityOutlinedIcon from '@mui/icons-material/SecurityOutlined';
import ApiOutlinedIcon from '@mui/icons-material/ApiOutlined';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface ArchitectureNode {
  name: string;
  type: string;
  icon: React.ReactNode;
}

export function ArchitectureDiagram() {
  const nodes: ArchitectureNode[] = [
    {
      name: 'Cliente',
      type: 'Frontend',
      icon: <CloudOutlinedIcon />,
    },
    {
      name: 'API Gateway',
      type: 'Gateway',
      icon: <HubOutlinedIcon />,
    },
    {
      name: 'Auth Service',
      type: 'Serviço',
      icon: <SecurityOutlinedIcon />,
    },
    {
      name: 'Order Service',
      type: 'Microserviço',
      icon: <ApiOutlinedIcon />,
    },
    {
      name: 'RabbitMQ',
      type: 'Mensageria',
      icon: <HubOutlinedIcon />,
    },
    {
      name: 'Payment Service',
      type: 'Serviço',
      icon: <ApiOutlinedIcon />,
    },
    {
      name: 'PostgreSQL',
      type: 'Banco',
      icon: <StorageOutlinedIcon />,
    },
  ];

  return (
    <Box
      sx={{
        mb: 6,
      }}
    >
      <Typography
        variant="h5"
        sx={{
          fontWeight: 600,
          color: '#1A1A1A',
          mb: 3,
        }}
      >
        Arquitetura Detectada
      </Typography>

      <Card
        elevation={0}
        sx={{
          bgcolor: '#FFFFFF',
          border: '1px solid #E8EAED',
          borderRadius: 2,
          p: 4,
        }}
      >
        <CardContent
          sx={{
            p: 0,
          }}
        >
          <Stack
            direction="row"
            spacing={2}
            sx={{
              alignItems: 'center',
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            {nodes.map((node, index) => (
              <Box
                key={node.name}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <Card
                  elevation={0}
                  sx={{
                    bgcolor: '#F7F8FA',
                    border: '1px solid #E8EAED',
                    borderRadius: 2,
                    minWidth: 140,
                    textAlign: 'center',
                    p: 2,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      borderColor: '#6D4CFF',
                      bgcolor: '#FFFFFF',
                      boxShadow: '0 4px 12px rgba(109, 76, 255, 0.12)',
                    },
                  }}
                >
                  <Box
                    sx={{
                      color: '#6D4CFF',
                      mb: 1,
                    }}
                  >
                    {node.icon}
                  </Box>

                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1A1A1A',
                      mb: 0.5,
                    }}
                  >
                    {node.name}
                  </Typography>

                  <Typography
                    variant="caption"
                    sx={{
                      color: '#64748B',
                    }}
                  >
                    {node.type}
                  </Typography>
                </Card>

                {index < nodes.length - 1 && (
                  <ArrowForwardIcon
                    sx={{
                      color: '#CBD5E1',
                      fontSize: 20,
                      mx: 1,
                    }}
                  />
                )}
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
