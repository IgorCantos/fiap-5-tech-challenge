'use client';

import { useState } from 'react';
import { Box, Grid } from '@mui/material';
import { AnalysisHeader } from './components/analysis-header';
import { MetricsCards } from './components/metrics-cards';
import { ArchitectureDiagram } from './components/architecture-diagram';
import { ComponentsList } from './components/components-list';
import { MainFlows } from './components/main-flows';
import { Vulnerabilities } from './components/vulnerabilities';
import { StrideAnalysis } from './components/stride-analysis';
import { AiRecommendations } from './components/ai-recommendations';
import { ExecutiveSummary } from './components/executive-summary';
import { ChatDrawer } from './components/chat-drawer';

export function ArchAnalysePage() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: '#F7F8FA',
      }}
    >
      <AnalysisHeader onChatOpen={() => setChatOpen(true)} />

      <Box
        sx={{
          maxWidth: '1400px',
          mx: 'auto',
          p: 3,
        }}
      >
        <MetricsCards />

        <Grid
          container
          spacing={3}
        >
          <Grid
            size={{
              xs: 12,
              lg: chatOpen ? 9 : 12,
            }}
          >
            <ArchitectureDiagram />
            <ComponentsList />
            <MainFlows />
            <Vulnerabilities />
            <StrideAnalysis />
            <AiRecommendations />
            <ExecutiveSummary />
          </Grid>

          {chatOpen && (
            <Grid
              size={{
                xs: 12,
                lg: 3,
              }}
            >
              <ChatDrawer
                open={chatOpen}
                onClose={() => setChatOpen(false)}
              />
            </Grid>
          )}
        </Grid>
      </Box>
    </Box>
  );
}