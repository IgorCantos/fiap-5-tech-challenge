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
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';

interface Vulnerability {
  name: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  icon: React.ReactNode;
  description: string;
  component: string;
  recommendation: string;
}

export function Vulnerabilities() {
  const vulnerabilities: Vulnerability[] = [
    {
      name: 'Ausência de mTLS',
      severity: 'Critical',
      icon: <ErrorIcon />,
      description: 'Serviços internos não possuem autenticação mútua',
      component: 'Todos os Microserviços',
      recommendation: 'Implementar mTLS entre serviços',
    },
    {
      name: 'Dados sem Criptografia',
      severity: 'Critical',
      icon: <ErrorIcon />,
      description: 'Dados sensíveis trafegam sem criptografia em repouso',
      component: 'PostgreSQL',
      recommendation: 'Habilitar TDE ou criptografia em nível de aplicação',
    },
    {
      name: 'Rate Limit Ausente',
      severity: 'High',
      icon: <WarningIcon />,
      description: 'API Gateway não possui limitação de requisições',
      component: 'API Gateway',
      recommendation: 'Configurar rate limit por IP e usuário',
    },
    {
      name: 'Logs Insuficientes',
      severity: 'High',
      icon: <WarningIcon />,
      description: 'Logs não possuem informações de auditoria completas',
      component: 'Todos os Serviços',
      recommendation: 'Implementar logs estruturados com contexto',
    },
    {
      name: 'Secrets Hardcoded',
      severity: 'Medium',
      icon: <InfoIcon />,
      description: 'Credenciais encontradas em código fonte',
      component: 'Auth Service',
      recommendation: 'Migrar para Secrets Manager',
    },
    {
      name: 'Dependências Desatualizadas',
      severity: 'Medium',
      icon: <InfoIcon />,
      description: 'Packages com vulnerabilidades conhecidas',
      component: 'Frontend',
      recommendation: 'Atualizar dependências e usar Snyk',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return '#DC2626';
      case 'High':
        return '#EA580C';
      case 'Medium':
        return '#D97706';
      case 'Low':
        return '#65A30D';
      default:
        return '#64748B';
    }
  };

  const getSeverityBgColor = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return '#FEE2E2';
      case 'High':
        return '#FFEDD5';
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
        Vulnerabilidades Encontradas
      </Typography>

      <Grid
        container
        spacing={2}
      >
        {vulnerabilities.map((vuln) => (
          <Grid
            key={vuln.name}
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
                border: vuln.severity === 'Critical'
                  ? '2px solid #DC2626'
                  : '1px solid #E8EAED',
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
                      bgcolor: getSeverityBgColor(vuln.severity),
                      color: getSeverityColor(vuln.severity),
                      width: 36,
                      height: 36,
                      mr: 2,
                    }}
                  >
                    {vuln.icon}
                  </Avatar>

                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: '#1A1A1A',
                      }}
                    >
                      {vuln.name}
                    </Typography>
                  </Box>

                  <Chip
                    label={vuln.severity}
                    size="small"
                    sx={{
                      bgcolor: getSeverityBgColor(vuln.severity),
                      color: getSeverityColor(vuln.severity),
                      fontWeight: 600,
                      fontSize: 11,
                    }}
                  />
                </Box>

                <Stack spacing={1.5}>
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                        fontWeight: 500,
                      }}
                    >
                      Descrição
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#1A1A1A',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {vuln.description}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                        fontWeight: 500,
                      }}
                    >
                      Componente
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#1A1A1A',
                      }}
                    >
                      {vuln.component}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#64748B',
                        fontWeight: 500,
                      }}
                    >
                      Recomendação
                    </Typography>

                    <Typography
                      variant="caption"
                      sx={{
                        color: '#1A1A1A',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {vuln.recommendation}
                    </Typography>
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
