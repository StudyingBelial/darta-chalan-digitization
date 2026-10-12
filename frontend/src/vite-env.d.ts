/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  electronAPI?: {
    isDesktopApp: boolean;
    getVersion: () => Promise<string>;
    listScannerDevices: () => Promise<Array<{ id: string; name: string; type: string; isDefault?: boolean }>>;
    scanFromDevice: (options: any) => Promise<{ success: boolean; message: string; dataUrl?: string }>;
  };
}
