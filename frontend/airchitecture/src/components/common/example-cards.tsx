'use client';

import {
  Box,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Stack,
  Typography,
} from '@mui/material';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import CloudQueueOutlinedIcon from '@mui/icons-material/CloudQueueOutlined';
import SyncAltOutlinedIcon from '@mui/icons-material/SyncAltOutlined';

const examples = [
  {
    title: 'Microserviços',
    subtitle: 'Arquitetura distribuída',
    icon: <AccountTreeOutlinedIcon color="primary" />,
  },
  {
    title: 'E-commerce',
    subtitle: 'Aplicação escalável',
    icon: <ShoppingCartOutlinedIcon color="success" />,
  },
  {
    title: 'Serverless',
    subtitle: 'Arquitetura em nuvem',
    icon: <CloudQueueOutlinedIcon sx={{ color: '#F97316' }} />,
  },
  {
    title: 'Fila de Mensagens',
    subtitle: 'Processamento assíncrono',
    icon: <SyncAltOutlinedIcon color="info" />,
  },
];

export function ExampleCards() {
  return (
    <Box>
      <Typography variant="h5">Diagramas de exemplo</Typography>

      <Typography color="text.secondary">
        Clique em um exemplo para analisar
      </Typography>

      <Stack
        direction={{
          xs: 'column',
          md: 'row',
        }}
        spacing={3}
      >
        {examples.map((item) => (
          <Card
            key={item.title}
            elevation={0}
            sx={{
              flex: 1,
              border: '1px solid #ECECF5',
              borderRadius: 4,
            }}
          >
            <CardActionArea>
              <CardMedia
                sx={{
                  height: 170,
                  bgcolor: '#F7F8FC',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Box
                  sx={{
                    width: '80%',
                    height: 110,
                    borderRadius: 2,
                    bgcolor: '#FFF',
                    border: '1px solid #E6E8F0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </Box>
              </CardMedia>

              <CardContent>
                <Typography>{item.title}</Typography>

                <Typography variant="body2" color="text.secondary">
                  {item.subtitle}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Stack>
    </Box>
  );
}
