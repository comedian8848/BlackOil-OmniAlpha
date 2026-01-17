import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Save, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

// Define Types matching Backend
interface AISettings {
  provider: 'openai' | 'anthropic' | 'local' | 'custom' | 'gemini' | 'deepseek';
  api_key: string;
  base_url: string;
  model_name: string;
  temperature: number;
  permission_level: 'consultant' | 'coding' | 'copilot';
}

interface TradingSettings {
  initial_capital: number;
  commission_rate: number;
  tax_rate: number;
  risk_free_rate: number;
}

interface SystemSettings {
  theme: 'light' | 'dark' | 'system';
  log_level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  auto_update_data: boolean;
}

interface AppSettings {
  ai: AISettings;
  trading: TradingSettings;
  system: SystemSettings;
}

const Settings: React.FC = () => {
  const { t } = useTranslation();
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Fetch Settings on Mount
  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/settings/');
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to load settings:', error);
      setMessage({ type: 'error', text: t('error') });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    setMessage(null);
    try {
      await axios.put('/api/settings/', settings);
      setMessage({ type: 'success', text: t('settings.save.success') });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setMessage({ type: 'error', text: t('settings.save.error') });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if(!window.confirm(t('settings.reset.confirm'))) return;
    setLoading(true);
    try {
      const response = await axios.post('/api/settings/reset');
      setSettings(response.data);
      setMessage({ type: 'success', text: 'Settings reset to defaults.' }); // Keep English for logs/untranslated
    } catch (error) {
       setMessage({ type: 'error', text: t('error') });
    } finally {
      setLoading(false);
    }
  }

  // --- Handlers for updates ---
  const updateAI = (key: keyof AISettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, ai: { ...settings.ai, [key]: value } });
  };

  const updateTrading = (key: keyof TradingSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, trading: { ...settings.trading, [key]: value } });
  };

  const updateSystem = (key: keyof SystemSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, system: { ...settings.system, [key]: value } });
  };

  if (loading) return <div className="p-8 text-center text-gray-500">{t('loading')}</div>;
  if (!settings) return <div className="p-8 text-center text-red-500">{t('error')}</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('settings.title')}</h1>
          <p className="text-gray-500 mt-1">{t('settings.subtitle')}</p>
        </div>
        <div className="flex gap-4">
            <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors"
                disabled={saving}
            >
                {t('settings.reset')}
            </button>
            <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
            >
                {saving ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                <Save className="w-4 h-4 mr-2" />
                )}
                {saving ? t('settings.saving') : t('settings.save')}
            </button>
        </div>
      </div>

      {/* Message Toast */}
      {message && (
        <div className={`p-4 rounded-md flex items-center ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 mr-2"/> : <AlertCircle className="w-5 h-5 mr-2"/>}
          {message.text}
        </div>
      )}

      {/* Grid Container */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Trading Settings */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
            <span className="w-1 h-6 bg-blue-500 mr-2 rounded-full"></span>
            {t('settings.trading.title')}
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.trading.capital')}</label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-400">¥</span>
                <input
                  type="number"
                  value={settings.trading.initial_capital}
                  onChange={(e) => updateTrading('initial_capital', parseFloat(e.target.value))}
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.trading.commission')}</label>
                    <input
                        type="number"
                        step="0.0001"
                        value={settings.trading.commission_rate}
                        onChange={(e) => updateTrading('commission_rate', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.trading.tax')}</label>
                    <input
                        type="number"
                        step="0.001"
                        value={settings.trading.tax_rate}
                        onChange={(e) => updateTrading('tax_rate', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
            </div>
             <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.trading.risk_free')}</label>
                <input
                    type="number"
                    step="0.01"
                    value={settings.trading.risk_free_rate}
                    onChange={(e) => updateTrading('risk_free_rate', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
            </div>
          </div>
        </section>

        {/* AI Settings */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
            <span className="w-1 h-6 bg-purple-500 mr-2 rounded-full"></span>
            {t('settings.ai.title')}
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.provider')}</label>
                  <select
                    value={settings.ai.provider}
                    onChange={(e) => updateAI('provider', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                  >
                    <option value="local">Local (Ollama/LlamaCpp)</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="gemini">Gemini (Google)</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="custom">Custom / Proxy</option>
                  </select>
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.permission')}</label>
                    <select
                        value={settings.ai.permission_level}
                        onChange={(e) => updateAI('permission_level', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    >
                        <option value="consultant">{t('settings.ai.permission.consultant')}</option>
                        <option value="coding">{t('settings.ai.permission.coding')}</option>
                        <option value="copilot">{t('settings.ai.permission.copilot')}</option>
                    </select>
                </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.model')}</label>
              <input
                type="text"
                value={settings.ai.model_name}
                onChange={(e) => updateAI('model_name', e.target.value)}
                placeholder="e.g. gpt-4-turbo or llama3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
             <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.key')}</label>
              <input
                type="password"
                value={settings.ai.api_key || ''}
                onChange={(e) => updateAI('api_key', e.target.value)}
                placeholder="sk-..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.base_url')}</label>
              <input
                type="text"
                value={settings.ai.base_url || ''}
                onChange={(e) => updateAI('base_url', e.target.value)}
                placeholder="https://api.openai.com/v1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.ai.temp')} ({settings.ai.temperature})</label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={settings.ai.temperature}
                    onChange={(e) => updateAI('temperature', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
            </div>
          </div>
        </section>

        {/* System Settings */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 md:col-span-2">
           <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
            <span className="w-1 h-6 bg-gray-500 mr-2 rounded-full"></span>
            {t('settings.system.title')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.system.theme')}</label>
              <select
                value={settings.system.theme}
                onChange={(e) => updateSystem('theme', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gray-500 focus:border-gray-500"
              >
                <option value="light">{t('settings.system.theme.light')}</option>
                <option value="dark">{t('settings.system.theme.dark')}</option>
                <option value="system">{t('settings.system.theme.system')}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.system.log_level')}</label>
               <select
                value={settings.system.log_level}
                onChange={(e) => updateSystem('log_level', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gray-500 focus:border-gray-500"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
             <div className="flex items-center pt-6">
                <input
                    id="auto-update"
                    type="checkbox"
                    checked={settings.system.auto_update_data}
                    onChange={(e) => updateSystem('auto_update_data', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="auto-update" className="ml-2 block text-sm text-gray-900">
                    {t('settings.system.auto_update')}
                </label>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default Settings;
