import { useState, useCallback } from 'react';

export type ZoomLevel = 'overview' | 'standard' | 'detailed';

export function useZoomLevel() {
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>('standard');

  const onViewportChange = useCallback((viewport: { zoom: number }) => {
    const z = viewport.zoom;
    if (z < 0.5) setZoomLevel('overview');
    else if (z > 1.2) setZoomLevel('detailed');
    else setZoomLevel('standard');
  }, []);

  return { zoomLevel, onViewportChange };
}
