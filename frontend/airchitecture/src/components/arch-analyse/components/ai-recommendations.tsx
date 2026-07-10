'use client';

import {
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ConstructionIcon from '@mui/icons-material/Construction';

interface Recommendation {
  title: string;
  priority: 'High' | 'Medium' | 'Low';
  impact: string;
  difficulty: string;
}

export function AiRecommendations() {
  const recommendations: Recommendation[] = [
    {
      title: 'Adicionar autenticação mTLS entre microsserviços',
      priority: 'High',
      impact: 'Alto',
      difficulty: 'Média',
    },
    {
      title: 'Criptografar comunicação interna com TLS 1.3',
      priority: 'High',
      impact: 'Alto',
      difficulty: 'Baixa',
    },
    {
      title: 'Adicionar Rate Limit no API Gateway',
      priority: 'High',
      impact: 'Médio',
      difficulty: 'Baixa',
    },
    {
      title: 'Habilitar logs centralizados com ELK Stack',
      priority: 'Medium',
      impact: 'Alto',
      difficulty: 'Média',
    },
    {
      title: 'Adicionar assinatura digital em eventos do RabbitMQ',
      priority: 'Medium',
      impact: 'Médio',
      difficulty: 'Alta',
    },
    {
      title: 'Implementar Secrets Manager (AWS Secrets Manager)',
      priority: 'High',
      impact: 'Alto',
      difficulty: 'Média',
    },
    {
      title: 'Configurar WAF para proteção contra ataques comuns',
      priority: 'Medium',
      impact: 'Médio',
      difficulty: 'Baixa',
    },
    {
      title: 'Implementar RBAC granular em todos os serviços',
      priority: 'High',
      impact: 'Alto',
      difficulty: 'Alta',
    },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High':
        return '#DC2626';
      case 'Medium':
        return '#D97706';
      case 'Low':
        return '#65A30D';
      default:
        return '#64748B';
    }
  };

  const getPriorityBgColor = (priority: string) => {
    switch (priority) {
      case 'High':
        return '#FEE2E2';
      case 'Medium':
        return '#FEF3C7';
      case 'Low':
        return '#ECFCCB';
      default:
        return '#F1F5F9';
    }
  };

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
        Recomendações da IA
      </Typography>

      <Stack spacing={2}>
        {recommendations.map((rec, index) => (
          <Card
            key={rec.title}
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
                  alignItems: 'flex-start',
                }}
              >
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    bgcolor: '#6D4CFF',
                    color: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 14,
                    fontWeight: 600,
                    mr: 2,
                    flexShrink: 0,
                  }}
                >
                  {index + 1}
                </Box>

                <Box sx={{ flex: 1 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: 1,
                      mb: 1.5,
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: '#1A1A1A',
                      }}
                    >
                      {rec.title}
                    </Typography>

                    <Chip
                      label={rec.priority}
                      size="small"
                      sx={{
                        bgcolor: getPriorityBgColor(rec.priority),
                        color: getPriorityColor(rec.priority),
                        fontWeight: 600,
                        fontSize: 11,
                      }}
                    />
                  </Box>

                  <Stack
                    direction="row"
                    spacing={3}
                    sx={{
                      flexWrap: 'wrap',
                    }}
                  >
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                      }}
                    >
                      <TrendingUpIcon
                        sx={{
                          fontSize: 16,
                          color: '#10B981',
                        }}
                      />

                      <Typography
                        variant="caption"
                        sx={{
                          color: '#64748B',
                        }}
                      >
                        Impacto: {rec.impact}
                      </Typography>
                    </Box>

                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                      }}
                    >
                      <ConstructionIcon
                        sx={{
                          fontSize: 16,
                          color: '#64748B',
                        }}
                      />

                      <Typography
                        variant="caption"
                        sx={{
                          color: '#64748B',
                        }}
                      >
                        Dificuldade: {rec.difficulty}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Box>
  );
}
