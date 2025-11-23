import { useEffect, useState } from 'react';
import { getSettings, updateSettings, getHHLoginUrl, getResumes, startBot } from '../api/endpoints';

export default function Dashboard() {
  const [settings, setSettings] = useState({
    search_text: '',
    resume_id: '',
    area_id: '113', // Default Russia
    salary: 0,
    cover_letter: ''
  });
  const [resumes, setResumes] = useState([]);
  const [isHHConnected, setIsHHConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Try fetching resumes to check connection and populate dropdown
      const resumesResp = await getResumes();
      setResumes(resumesResp.data);
      setIsHHConnected(true);

      // Fetch existing settings
      const settingsResp = await getSettings();
      if (settingsResp.data) {
        setSettings(settingsResp.data);
      }
    } catch (error) {
      // If fetching resumes fails, likely not connected to HH
      setIsHHConnected(false);
    }
  };

  const handleConnectHH = async () => {
    const { data } = await getHHLoginUrl();
    window.location.href = data.url;
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await updateSettings(settings);
      alert('Settings saved successfully!');
    } catch (e) {
      alert('Error saving settings');
    }
  };

  const handleRunBot = async () => {
    setLoading(true);
    try {
      await startBot();
      alert('Task started! Check console logs for progress.');
    } catch (e) {
      alert('Failed to start task');
    } finally {
      setLoading(false);
    }
  };

  if (!isHHConnected) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h2 className="text-2xl font-bold mb-4">Connect HeadHunter</h2>
        <p className="text-gray-600 mb-6">You need to link your HH.ru account to start applying.</p>
        <button
          onClick={handleConnectHH}
          className="bg-red-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-red-700 transition"
        >
          Login with HH.ru
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Settings Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-bold mb-4 border-b pb-2">Search Settings</h3>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Resume</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={settings.resume_id}
              onChange={(e) => setSettings({ ...settings, resume_id: e.target.value })}
              required
            >
              <option value="">Select a resume</option>
              {resumes.map((res) => (
                <option key={res.id} value={res.id}>
                  {res.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Search Query</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={settings.search_text}
              onChange={(e) => setSettings({ ...settings, search_text: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Minimum Salary</label>
            <input
              type="number"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={settings.salary || ''}
              onChange={(e) => setSettings({ ...settings, salary: parseInt(e.target.value) || 0 })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Area ID (e.g., 1 for Moscow)</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={settings.area_id}
              onChange={(e) => setSettings({ ...settings, area_id: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Cover Letter</label>
            <textarea
              rows={4}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={settings.cover_letter || ''}
              onChange={(e) => setSettings({ ...settings, cover_letter: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            Save Settings
          </button>
        </form>
      </div>

      {/* Control Panel */}
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-bold mb-4 border-b pb-2">Actions</h3>
          <p className="text-gray-600 mb-4">
            Manually trigger the search and apply process based on the settings above.
          </p>
          <button
            onClick={handleRunBot}
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md text-white font-bold transition ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {loading ? 'Processing...' : 'Run Auto Applier Now'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-bold mb-2">Instructions</h3>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-2">
                <li>Select the Resume you want to use for applications.</li>
                <li>Enter the job title you are looking for (e.g. "Python Developer").</li>
                <li>Enter minimum salary (optional).</li>
                <li>Click "Save Settings".</li>
                <li>Click "Run Auto Applier Now" to start applying to the top 20 vacancies.</li>
            </ul>
        </div>
      </div>
    </div>
  );
}