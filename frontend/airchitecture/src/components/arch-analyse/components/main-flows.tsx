'use client';

import {
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface Flow {
  name: string;
  sequence: string[];
  protocol: string;
  auth: string;
  notes: string;
}

export function MainFlows() {
  const flows: Flow[] = [
    {
      name: 'Autenticação',
      sequence: ['Frontend', 'API Gateway', 'Auth Service', 'PostgreSQL'],
      protocol: 'HTTPS',
      auth: 'JWT',
      notes: 'Token válido por 1h',
    },
    {
      name: 'Criação de Pedido',
      sequence: ['Frontend', 'API Gateway', 'Order Service', 'RabbitMQ', 'Payment Service'],
      protocol: 'HTTPS',
      auth: 'JWT',
      notes: 'Processamento assíncrono',
    },
    {
      name: 'Consulta de Produtos',
      sequence: ['Frontend', 'API Gateway', 'Order Service', 'Redis', 'PostgreSQL'],
      protocol: 'HTTPS',
      auth: 'JWT',
      notes: 'Cache de 5 minutos',
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
        Fluxos Principais
      </Typography>

      <Stack spacing={2}>
        {flows.map((flow) => (
          <Card
            key={flow.name}
            elevation={0}
            sx={{
              bgcolor: '#FFFFFF',
              border: '1px solid #E8EAED',
              borderRadius: 2,
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
                  flexWrap: 'wrap',
                  gap: 1,
                }}
              >
                {flow.sequence.map((item, index) => (
                  <Box
                    key={item}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                    }}
                  >
                    <Chip
                      label={item}
                      size="small"
                      sx={{
                        bgcolor: '#F7F8FA',
                        color: '#1A1A1A',
                        fontWeight: 500,
                        fontSize: 12,
                      }}
                    />

                    {index < flow.sequence.length - 1 && (
                      <ArrowForwardIcon
                        sx={{
                          color: '#CBD5E1',
                          fontSize: 16,
                          mx: 0.5,
                        }}
                      />
                    )}
                  </Box>
                ))}
              </Box>

              <Stack
                direction="row"
                spacing={3}
                sx={{
                  flexWrap: 'wrap',
                }}
              >
                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#64748B',
                      mr: 1,
                    }}
                  >
                    Protocolo:
                  </Typography>

                  <Chip
                    label={flow.protocol}
                    size="small"
                    sx={{
                      bgcolor: '#E0E7FF',
                      color: '#4338CA',
                      fontSize: 11,
                      height: 24,
                    }}
                  />
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#64748B',
                      mr: 1,
                    }}
                  >
                    Autenticação:
                  </Typography>

                  <Chip
                    label={flow.auth}
                    size="small"
                    sx={{
                      bgcolor: '#DCFCE7',
                      color: '#166534',
                      fontSize: 11,
                      height: 24,
                    }}
                  />
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#64748B',
                    }}
                  >
                    {flow.notes}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Box>
  );
}
