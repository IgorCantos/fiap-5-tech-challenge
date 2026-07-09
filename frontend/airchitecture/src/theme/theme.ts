import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6C4CF1',
    },
    background: {
      default: '#FAFAFE',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#20263A',
      secondary: '#6D7280',
    },
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
    h2: {
      fontWeight: 800,
    },
    h5: {
      fontWeight: 700,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 16,
  },
});
