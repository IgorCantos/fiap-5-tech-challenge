'use client';

import { Box, Card, CardContent, Container, Stack, Typography } from '@mui/material';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import { Navbar } from '@/components/layout/navbar';
import { Footer } from '@/components/layout/footer';
import { UploadZone } from '@/components/common/upload-zone';
import { ExampleCards } from '@/components/common/example-cards';

export function HomePage() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background:
          'radial-gradient(circle at top, rgba(108,76,241,.10), transparent 35%), #FAFAFE',
      }}
    >
      <Navbar />

      <Container maxWidth="lg">
        <Stack
          spacing={6}
          sx={{
            alignItems: 'center',
            pt: 10,
            pb: 10,
          }}
        >
          <Stack
            spacing={3}
            sx={{
              alignItems: 'center',
            }}
          >
            <Typography
              variant="h2"
              align="center"
              sx={{
                fontSize: {
                  xs: 38,
                  md: 56,
                },
                lineHeight: 1.15,
              }}
            >
              Entenda sua arquitetura
              <br />
              com inteligência artificial
            </Typography>

            <Typography
              align="center"
              color="text.secondary"
              sx={{
                fontSize: 18,
                maxWidth: 620,
              }}
            >
              Faça upload do seu diagrama de arquitetura e receba uma
              análise completa com descrição, componentes, riscos e
              relatório STRIDE.
            </Typography>
          </Stack>

          <UploadZone />

          <ExampleCards />

          <Card
            elevation={0}
            sx={{
              width: '100%',
              maxWidth: 900,
              bgcolor: '#F3EEFF',
              borderRadius: 5,
            }}
          >
            <CardContent
              sx={{
                py: 4,
              }}
            >
              <Stack
                direction="row"
                spacing={3}
                sx={{
                  alignItems: 'center',
                }}
              >
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    bgcolor: '#FFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <ShieldOutlinedIcon
                    color="primary"
                    fontSize="large"
                  />
                </Box>

                <Box>
                  <Typography
                    color="primary"
                  >
                    Seus diagramas são processados com segurança
                  </Typography>

                  <Typography color="text.secondary">
                    Não armazenamos suas imagens. Todo o processamento
                    é feito de forma segura e privada.
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Footer />
        </Stack>
      </Container>
    </Box>
  );
}
