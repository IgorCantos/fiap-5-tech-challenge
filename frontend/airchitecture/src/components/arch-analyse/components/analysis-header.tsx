'use client';

import {
  AppBar,
  Box,
  Button,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ChatOutlinedIcon from '@mui/icons-material/ChatOutlined';

interface AnalysisHeaderProps {
  onChatOpen: () => void;
}

export function AnalysisHeader({ onChatOpen }: AnalysisHeaderProps) {
  return (
    <AppBar
      elevation={0}
      position="sticky"
      sx={{
        bgcolor: '#FFFFFF',
        borderBottom: '1px solid #E8EAED',
        height: 56,
      }}
    >
      <Toolbar
        sx={{
          minHeight: 56,
          px: 3,
        }}
      >
        <Stack
          direction="row"
          spacing={2}
          sx={{
            alignItems: 'center',
          }}
        >
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 2,
              bgcolor: '#6D4CFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AutoAwesomeIcon
              sx={{
                fontSize: 18,
                color: '#FFFFFF',
              }}
            />
          </Box>

          <Typography
            variant="body2"
            sx={{
              fontWeight: 600,
              color: '#1A1A1A',
            }}
          >
            Airchitecture AI
          </Typography>
        </Stack>

        <Box sx={{ flex: 1 }} />

        <Button
          variant="outlined"
          startIcon={<ChatOutlinedIcon sx={{ fontSize: 18 }} />}
          onClick={onChatOpen}
          sx={{
            borderRadius: 2,
            px: 2.5,
            py: 1,
            fontSize: 14,
            fontWeight: 500,
            borderColor: '#E8EAED',
            color: '#64748B',
            bgcolor: 'transparent',
            '&:hover': {
              borderColor: '#6D4CFF',
              bgcolor: 'rgba(109, 76, 255, 0.04)',
            },
          }}
        >
          Conversar com a IA
        </Button>
      </Toolbar>
    </AppBar>
  );
}
