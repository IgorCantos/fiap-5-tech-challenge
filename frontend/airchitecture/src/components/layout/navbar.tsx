'use client';

import {
  AppBar,
  Box,
  Button,
  Container,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

export function Navbar() {
  return (
    <AppBar
      position="static"
      elevation={0}
      color="transparent"
      sx={{
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(0,0,0,.04)',
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ py: 2 }}>
          <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
            <Box
              sx={{
                width: 42,
                height: 42,
                borderRadius: 3,
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <AutoAwesomeIcon />
            </Box>

            <Box>
              <Typography>AIrchitecture</Typography>
            </Box>
          </Stack>

          <Box sx={{ flex: 1 }} />

          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              sx={{
                borderRadius: 3,
                px: 3,
              }}
            >
              Entrar
            </Button>

            <Button
              variant="contained"
              sx={{
                borderRadius: 3,
                px: 3,
              }}
            >
              Criar conta
            </Button>
          </Stack>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
