'use client';

import {
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import CloudOutlinedIcon from '@mui/icons-material/CloudOutlined';
import HubOutlinedIcon from '@mui/icons-material/HubOutlined';
import StorageOutlinedIcon from '@mui/icons-material/StorageOutlined';
import ApiOutlinedIcon from '@mui/icons-material/ApiOutlined';
import SecurityOutlinedIcon from '@mui/icons-material/SecurityOutlined';
import WebIcon from '@mui/icons-material/Web';
import DnsIcon from '@mui/icons-material/Dns';
import RouterIcon from '@mui/icons-material/Router';

interface Component {
  icon: React.ReactNode;
  name: string;
  type: string;
  language: string;
  framework: string;
  risk: string;
  description: string;
}

export function ComponentsList() {
  const components: Component[] = [
    {
      icon: <WebIcon />,
      name: 'React Frontend',
      type: 'Frontend',
      language: 'TypeScript',
      framework: 'Next.js',
      risk: 'Baixo',
      description: 'Interface de usuário responsiva com SSR e SSG',
    },
    {
      icon: <HubOutlinedIcon />,
      name: 'API Gateway',
      type: 'Gateway',
      language: 'TypeScript',
      framework: 'Express',
      risk: 'Médio',
      description: 'Roteamento de requisições e autenticação centralizada',
    },
    {
      icon: <SecurityOutlinedIcon />,
      name: 'Auth Service',
      type: 'Serviço',
      language: 'TypeScript',
      framework: 'NestJS',
      risk: 'Alto',
      description: 'Gerenciamento de autenticação e autorização JWT',
    },
    {
      icon: <ApiOutlinedIcon />,
      name: 'Order Service',
      type: 'Microserviço',
      language: 'TypeScript',
      framework: 'NestJS',
      risk: 'Médio',
      description: 'Processamento de pedidos e gestão de carrinho',
    },
    {
      icon: <RouterIcon />,
      name: 'RabbitMQ',
      type: 'Mensageria',
      language: 'Erlang',
      framework: 'AMQP',
      risk: 'Baixo',
      description: 'Broker de mensagens para comunicação assíncrona',
    },
    {
      icon: <ApiOutlinedIcon />,
      name: 'Payment Service',
      type: 'Serviço',
      language: 'TypeScript',
      framework: 'NestJS',
      risk: 'Alto',
      description: 'Integração com gateways de pagamento',
    },
    {
      icon: <StorageOutlinedIcon />,
      name: 'PostgreSQL',
      type: 'Banco',
      language: 'SQL',
      framework: 'PostgreSQL 15',
      risk: 'Baixo',
      description: 'Banco de dados relacional principal',
    },
    {
      icon: <CloudOutlinedIcon />,
      name: 'Redis',
      type: 'Cache',
      language: 'C',
      framework: 'Redis 7',
      risk: 'Baixo',
      description: 'Cache de sessões e dados temporários',
    },
    {
      icon: <DnsIcon />,
      name: 'Nginx',
      type: 'Load Balancer',
      language: 'C',
      framework: 'Nginx',
      risk: 'Baixo',
      description: 'Balanceamento de carga e servidor estático',
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
        Componentes Detectados
      </Typography>

      <Grid
        container
        spacing={2}
      >
        {components.map((component) => (
          <Grid
            key={component.name}
            size={{
              xs: 12,
              sm: 6,
              md: 4,
              lg: 4,
            }}
          >
            <Card
              elevation={0}
              sx={{
                bgcolor: '#FFFFFF',
                border: '1px solid #E8EAED',
                borderRadius: 2,
                height: '100%',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  borderColor: '#6D4CFF',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
                },
              }}
            >
              <CardContent
                sx={{
                  p: 2.5,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mb: 2,
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: '#F7F8FA',
                      color: '#6D4CFF',
                      width: 40,
                      height: 40,
                      mr: 2,
                    }}
                  >
                    {component.icon}
                  </Avatar>

                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: '#1A1A1A',
                      }}
                    >
                      {component.name}
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      {component.type}
                    </Typography>
                  </Box>

                  <Chip
                    label={component.risk}
                    size="small"
                    color={
                      component.risk === 'Alto'
                        ? 'error'
                        : component.risk === 'Médio'
                        ? 'warning'
                        : 'success'
                    }
                    sx={{
                      fontWeight: 500,
                      fontSize: 11,
                    }}
                  />
                </Box>

                <Stack
                  spacing={1}
                  sx={{
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      Linguagem
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 500,
                        color: '#1A1A1A',
                      }}
                    >
                      {component.language}
                    </Typography>
                  </Box>

                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      Framework
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 500,
                        color: '#1A1A1A',
                      }}
                    >
                      {component.framework}
                    </Typography>
                  </Box>
                </Stack>

                <Typography
                  variant="caption"
                  sx={{
                    color: '#64748B',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {component.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
