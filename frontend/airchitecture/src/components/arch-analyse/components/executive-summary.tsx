'use client';

import {
  Box,
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import StarIcon from '@mui/icons-material/Star';

export function ExecutiveSummary() {
  const score = 68;

  return (
    <Box>
      <Typography
        variant="h5"
        sx={{
          fontWeight: 600,
          color: '#1A1A1A',
          mb: 3,
        }}
      >
        Resumo Executivo
      </Typography>

      <Card
        elevation={0}
        sx={{
          bgcolor: '#FFFFFF',
          border: '1px solid #E8EAED',
          borderRadius: 2,
        }}
      >
        <CardContent
          sx={{
            p: 3,
          }}
        >
          <Grid
            container
            spacing={3}
          >
            <Grid
              size={{
                xs: 12,
                md: 6,
                lg: 3,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 2,
                }}
              >
                <CheckCircleIcon
                  sx={{
                    fontSize: 24,
                    color: '#10B981',
                  }}
                />

                <Box>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1A1A1A',
                      mb: 1,
                    }}
                  >
                    Pontos Fortes
                  </Typography>

                  <Stack spacing={0.5}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Arquitetura em microserviços
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Uso de mensageria assíncrona
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Separação de responsabilidades
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Cache implementado (Redis)
                    </Typography>
                  </Stack>
                </Box>
              </Box>
            </Grid>

            <Grid
              size={{
                xs: 12,
                md: 6,
                lg: 3,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 2,
                }}
              >
                <WarningIcon
                  sx={{
                    fontSize: 24,
                    color: '#F59E0B',
                  }}
                />

                <Box>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1A1A1A',
                      mb: 1,
                    }}
                  >
                    Principais Riscos
                  </Typography>

                  <Stack spacing={0.5}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Ausência de mTLS entre serviços
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Dados sem criptografia em repouso
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Rate limit não configurado
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      • Logs insuficientes para auditoria
                    </Typography>
                  </Stack>
                </Box>
              </Box>
            </Grid>

            <Grid
              size={{
                xs: 12,
                md: 6,
                lg: 3,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 2,
                }}
              >
                <PriorityHighIcon
                  sx={{
                    fontSize: 24,
                    color: '#DC2626',
                  }}
                />

                <Box>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1A1A1A',
                      mb: 1,
                    }}
                  >
                    Ações Prioritárias
                  </Typography>

                  <Stack spacing={0.5}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      1. Implementar mTLS
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      2. Criptografar banco de dados
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      3. Configurar rate limit
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      4. Migrar secrets para manager
                    </Typography>
                  </Stack>
                </Box>
              </Box>
            </Grid>

            <Grid
              size={{
                xs: 12,
                md: 6,
                lg: 3,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    width: 120,
                    height: 120,
                    borderRadius: '50%',
                    bgcolor: score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : '#DC2626',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                  }}
                >
                  <StarIcon
                    sx={{
                      position: 'absolute',
                      fontSize: 80,
                      color: 'rgba(255, 255, 255, 0.2)',
                    }}
                  />

                  <Typography
                    variant="h3"
                    sx={{
                      fontWeight: 700,
                      color: '#FFFFFF',
                      zIndex: 1,
                    }}
                  >
                    {score}
                  </Typography>
                </Box>

                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#1A1A1A',
                    textAlign: 'center',
                  }}
                >
                  Nota Geral da Arquitetura
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}
