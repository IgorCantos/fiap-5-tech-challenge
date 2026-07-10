'use client';

import { useRouter } from 'next/navigation';
import {
  Box,
  Card,
  CardActionArea,
  Stack,
  Typography,
} from '@mui/material';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';

export function UploadZone() {
  const router = useRouter();

  return (
    <Card
      elevation={0}
      sx={{
        width: '100%',
        maxWidth: 900,
        border: '2px dashed #B99BFF',
        borderRadius: 5,
        bgcolor: '#FFF',
      }}
    >
      <CardActionArea
        sx={{
          py: 10,
        }}
        onClick={() => router.push('/arch-analyse')}
      >
        <Stack
          spacing={3}
          sx={{
            alignItems: 'center',
          }}
        >
          <Box
            sx={{
              width: 90,
              height: 90,
              borderRadius: '50%',
              bgcolor: 'rgba(108,76,241,.10)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CloudUploadOutlinedIcon
              color="primary"
              sx={{ fontSize: 48 }}
            />
          </Box>

          <Box
            sx={{
              textAlign: 'center',
            }}
          >
            <Typography variant="h5">
              <b>Arraste e solte sua imagem aqui</b>
            </Typography>

            <Typography color="text.secondary">
              ou clique para selecionar
            </Typography>

            <Typography
              variant="body2"
              sx={{ mt: 2 }}
              color="text.secondary"
            >
              Suporta PNG, JPG, JPEG (máx. 10MB)
            </Typography>
          </Box>
        </Stack>
      </CardActionArea>
    </Card>
  );
}
