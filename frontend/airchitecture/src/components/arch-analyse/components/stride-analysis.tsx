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
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit';
import HistoryIcon from '@mui/icons-material/History';
import VisibilityIcon from '@mui/icons-material/Visibility';
import BlockIcon from '@mui/icons-material/Block';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

interface StrideCategory {
  name: string;
  icon: React.ReactNode;
  description: string;
  threats: string[];
  criticality: 'High' | 'Medium' | 'Low';
  recommendations: string[];
}

export function StrideAnalysis() {
  const categories: StrideCategory[] = [
    {
      name: 'Spoofing',
      icon: <PersonIcon />,
      description: 'Impersonação de identidade',
      threats: [
        'Serviços sem autenticação mútua',
        'Tokens JWT sem verificação de assinatura',
        'APIs públicas sem rate limiting',
      ],
      criticality: 'High',
      recommendations: [
        'Implementar mTLS entre serviços',
        'Validar assinatura de tokens',
        'Adicionar autenticação em todas as APIs',
      ],
    },
    {
      name: 'Tampering',
      icon: <EditIcon />,
      description: 'Alteração de dados',
      threats: [
        'Mensagens sem assinatura digital',
        'Dados em trânsito sem criptografia',
        'Logs sem integridade',
      ],
      criticality: 'High',
      recommendations: [
        'Assinar mensagens com HMAC',
        'Forçar HTTPS em todas as conexões',
        'Implementar checksum em logs',
      ],
    },
    {
      name: 'Repudiation',
      icon: <HistoryIcon />,
      description: 'Negação de ações',
      threats: [
        'Logs insuficientes para auditoria',
        'Ausência de rastreamento de ações',
        'Sem registro de quem fez o quê',
      ],
      criticality: 'Medium',
      recommendations: [
        'Implementar logs estruturados',
        'Adicionar contexto de usuário em logs',
        'Usar sistema de auditoria centralizado',
      ],
    },
    {
      name: 'Information Disclosure',
      icon: <VisibilityIcon />,
      description: 'Vazamento de informações',
      threats: [
        'Dados sensíveis em logs',
        'Respostas com informações excessivas',
        'Dados sem criptografia em repouso',
      ],
      criticality: 'High',
      recommendations: [
        'Sanitizar dados sensíveis em logs',
        'Limitar informações em respostas',
        'Criptografar banco de dados',
      ],
    },
    {
      name: 'Denial of Service',
      icon: <BlockIcon />,
      description: 'Indisponibilidade de serviço',
      threats: [
        'Ausência de rate limiting',
        'Sem proteção contra DDoS',
        'Recursos não limitados',
      ],
      criticality: 'Medium',
      recommendations: [
        'Configurar rate limiting',
        'Usar WAF e proteção DDoS',
        'Limitar recursos por requisição',
      ],
    },
    {
      name: 'Elevation of Privilege',
      icon: <AdminPanelSettingsIcon />,
      description: 'Escalada de privilégios',
      threats: [
        'Permissões excessivas entre serviços',
        'Sem validação de roles',
        'Tokens com escopo muito amplo',
      ],
      criticality: 'High',
      recommendations: [
        'Implementar RBAC granular',
        'Validar roles em cada operação',
        'Usar tokens com escopo mínimo',
      ],
    },
  ];

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
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

  const getCriticalityBgColor = (criticality: string) => {
    switch (criticality) {
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
        Análise STRIDE
      </Typography>

      <Grid
        container
        spacing={2}
      >
        {categories.map((category) => (
          <Grid
            key={category.name}
            size={{
              xs: 12,
              sm: 6,
              md: 4,
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
                    {category.icon}
                  </Avatar>

                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: '#1A1A1A',
                      }}
                    >
                      {category.name}
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                      }}
                    >
                      {category.description}
                    </Typography>
                  </Box>

                  <Chip
                    label={category.criticality}
                    size="small"
                    sx={{
                      bgcolor: getCriticalityBgColor(category.criticality),
                      color: getCriticalityColor(category.criticality),
                      fontWeight: 600,
                      fontSize: 11,
                    }}
                  />
                </Box>

                <Stack spacing={2}>
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                        fontWeight: 500,
                        mb: 1,
                        display: 'block',
                      }}
                    >
                      Ameaças Encontradas
                    </Typography>

                    <Stack spacing={0.5}>
                      {category.threats.map((threat) => (
                        <Typography
                          key={threat}
                          variant="caption"
                          sx={{
                            color: '#1A1A1A',
                            pl: 1,
                            borderLeft: '2px solid #E8EAED',
                          }}
                        >
                          {threat}
                        </Typography>
                      ))}
                    </Stack>
                  </Box>

                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                        fontWeight: 500,
                        mb: 1,
                        display: 'block',
                      }}
                    >
                      Recomendações
                    </Typography>

                    <Stack spacing={0.5}>
                      {category.recommendations.map((rec) => (
                        <Typography
                          key={rec}
                          variant="caption"
                          sx={{
                            color: '#1A1A1A',
                            pl: 1,
                            borderLeft: '2px solid #6D4CFF',
                          }}
                        >
                          {rec}
                        </Typography>
                      ))}
                    </Stack>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
