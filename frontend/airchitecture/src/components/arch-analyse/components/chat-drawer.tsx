'use client';

import { useState } from 'react';
import {
  Avatar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';

interface ChatMessage {
  sender: 'ia' | 'user';
  text: string;
}

interface ChatDrawerProps {
  open: boolean;
  onClose: () => void;
}

export function ChatDrawer({ open, onClose }: ChatDrawerProps) {
  const [message, setMessage] = useState('');

  const chat: ChatMessage[] = [
    {
      sender: 'user',
      text: 'Explique o fluxo de autenticação.',
    },
    {
      sender: 'ia',
      text: 'O fluxo de autenticação atual funciona da seguinte maneira: O frontend envia credenciais para o API Gateway via HTTPS. O Gateway valida as credenciais e encaminha para o Auth Service. O Auth Service verifica no PostgreSQL e retorna um token JWT válido por 1 hora. No entanto, identifiquei que não há autenticação mútua (mTLS) entre serviços internos, o que representa um risco de segurança significativo.',
    },
    {
      sender: 'user',
      text: 'Quais vulnerabilidades são mais críticas?',
    },
    {
      sender: 'ia',
      text: 'As vulnerabilidades mais críticas são: 1) Ausência de mTLS entre microsserviços - permite que qualquer serviço possa se passar por outro. 2) Dados sem criptografia em repouso no PostgreSQL - informações sensíveis estão expostas caso haja acesso físico ao banco. 3) Rate limit ausente no API Gateway - vulnerável a ataques DDoS. Recomendo priorizar a implementação de mTLS e criptografia do banco de dados.',
    },
    {
      sender: 'user',
      text: 'Como reduzir os riscos encontrados?',
    },
    {
      sender: 'ia',
      text: 'Para reduzir os riscos, sugiro as seguintes ações imediatas: 1) Implementar mTLS usando certificados gerenciados pelo serviço. 2) Habilitar criptografia TDE no PostgreSQL ou criptografar dados sensíveis em nível de aplicação. 3) Configurar rate limiting por IP e usuário no API Gateway. 4) Migrar secrets hardcoded para AWS Secrets Manager. 5) Implementar logs estruturados com contexto para auditoria. Essas ações elevariam significativamente a segurança da arquitetura.',
    },
  ];

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      //@ts-ignore
      PaperProps={{
        sx: {
          width: 420,
          borderLeft: '1px solid #E8EAED',
          bgcolor: '#FFFFFF',
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2.5,
          borderBottom: '1px solid #E8EAED',
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
              position: 'relative',
            }}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                bgcolor: '#6D4CFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AutoAwesomeIcon
                sx={{
                  fontSize: 20,
                  color: '#FFFFFF',
                }}
              />
            </Box>

            <Box
              sx={{
                position: 'absolute',
                bottom: -2,
                right: -2,
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: '#10B981',
                border: '2px solid #FFFFFF',
              }}
            />
          </Box>

          <Box>
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                color: '#1A1A1A',
              }}
            >
              Assistente de Arquitetura
            </Typography>

            <Stack
              direction="row"
              spacing={1}
              sx={{
                alignItems: 'center',
              }}
            >
              <Box
                sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  bgcolor: '#10B981',
                }}
              />

              <Typography
                variant="caption"
                sx={{
                  color: '#10B981',
                  fontWeight: 500,
                }}
              >
                Online
              </Typography>
            </Stack>
          </Box>
        </Stack>

        <IconButton
          onClick={onClose}
          sx={{
            color: '#64748B',
          }}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      <Divider />

      <Box
        sx={{
          flex: 1,
          p: 2,
          overflowY: 'auto',
          bgcolor: '#F7F8FA',
        }}
      >
        <Stack spacing={2}>
          {chat.map((msg, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent:
                  msg.sender === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  maxWidth: '85%',
                  borderRadius: 2,
                  bgcolor:
                    msg.sender === 'user'
                      ? '#6D4CFF'
                      : '#FFFFFF',
                  color: msg.sender === 'user' ? '#FFFFFF' : '#1A1A1A',
                  border:
                    msg.sender === 'user'
                      ? 'none'
                      : '1px solid #E8EAED',
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    lineHeight: 1.5,
                  }}
                >
                  {msg.text}
                </Typography>
              </Paper>
            </Box>
          ))}
        </Stack>
      </Box>

      <Divider />

      <Box
        sx={{
          p: 2,
          bgcolor: '#FFFFFF',
        }}
      >
        <Stack
          direction="row"
          spacing={1.5}
          sx={{
            alignItems: 'flex-end',
          }}
        >
          <TextField
            fullWidth
            multiline
            maxRows={4}
            size="small"
            placeholder="Pergunte sobre a arquitetura..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                bgcolor: '#F7F8FA',
                '& fieldset': {
                  borderColor: '#E8EAED',
                },
                '&:hover fieldset': {
                  borderColor: '#6D4CFF',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#6D4CFF',
                },
              },
            }}
          />

          <IconButton
            color="primary"
            sx={{
              bgcolor: '#6D4CFF',
              color: '#FFFFFF',
              borderRadius: 2,
              p: 1.5,
              '&:hover': {
                bgcolor: '#5A3FDB',
              },
            }}
          >
            <SendIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Stack>
      </Box>
    </Drawer>
  );
}
