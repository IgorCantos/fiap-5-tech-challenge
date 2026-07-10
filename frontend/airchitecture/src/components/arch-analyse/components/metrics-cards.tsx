'use client';

import { useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
} from '@mui/material';

interface MetricCard {
  title: string;
  value: string;
  color: string;
  icon: string;
}

export function MetricsCards() {
  const cards = useMemo<MetricCard[]>(
    () => [
      {
        title: 'Componentes',
        value: '17',
        color: '#6D4CFF',
        icon: '📦',
      },
      {
        title: 'Fluxos',
        value: '8',
        color: '#10B981',
        icon: '🔄',
      },
      {
        title: 'Vulnerabilidades',
        value: '12',
        color: '#F59E0B',
        icon: '⚠️',
      },
      {
        title: 'Bancos de Dados',
        value: '3',
        color: '#3B82F6',
        icon: '🗄️',
      },
      {
        title: 'Integrações',
        value: '5',
        color: '#8B5CF6',
        icon: '🔗',
      },
      {
        title: 'Risco Geral',
        value: 'Alto',
        color: '#EF4444',
        icon: '🔴',
      },
    ],
    []
  );

  return (
    <Box>
      <Box
        sx={{
          mb: 4,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 600,
            color: '#1A1A1A',
            mb: 1,
          }}
        >
          Sistema de E-commerce
        </Typography>

        <Typography
          variant="body2"
          sx={{
            color: '#64748B',
          }}
        >
          Análise realizada em 10 de julho de 2026 às 19:58
        </Typography>
      </Box>

      <Grid
        container
        spacing={2}
      >
        {cards.map((card) => (
          <Grid
            key={card.title}
            size={{
              xs: 12,
              sm: 6,
              md: 4,
              lg: 2,
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
                  borderColor: card.color,
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
                    justifyContent: 'space-between',
                    mb: 2,
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#64748B',
                      fontWeight: 500,
                      textTransform: 'uppercase',
                      letterSpacing: 0.5,
                    }}
                  >
                    {card.title}
                  </Typography>

                  <Box
                    sx={{
                      fontSize: 20,
                    }}
                  >
                    {card.icon}
                  </Box>
                </Box>

                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: card.color,
                    mb: 1,
                  }}
                >
                  {card.value}
                </Typography>

                <Box
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    bgcolor: '#F7F8FA',
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      height: '100%',
                      width: '75%',
                      bgcolor: card.color,
                      borderRadius: 2,
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
