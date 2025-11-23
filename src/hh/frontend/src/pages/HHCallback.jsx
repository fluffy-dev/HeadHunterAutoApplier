import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { sendHHCode } from '../api/endpoints';

export default function HHCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    if (code) {
      sendHHCode(code)
        .then(() => navigate('/'))
        .catch(() => alert('Failed to connect HH'));
    }
  }, [searchParams, navigate]);

  return (
    <div className="flex justify-center items-center h-screen">
      <p className="text-xl">Connecting to HeadHunter...</p>
    </div>
  );
}