import { useState } from 'react';
import axios from 'axios';

function ResumeUpload() {
    const [jobId, setJobId] = useState('');
    const [resume, setResume] = useState(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        setResume(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        if (!resume || !jobId) {
            setError('Please provide a job ID and resume file');
            return;
        }
        const formData = new FormData();
        formData.append('job_id', jobId);
        formData.append('resume', resume);

        try {
            const response = await axios.post('http://localhost:8000/api/apply', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setMessage(response.data.message);
            setJobId('');
            setResume(null);
            e.target.reset();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload resume');
        }
    };

    return (
        <div>
            <h2 className="text-xl font-semibold mb-4">Upload Resume</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Job ID</label>
                    <input
                        type="number"
                        value={jobId}
                        onChange={(e) => setJobId(e.target.value)}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Resume (PDF)</label>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="mt-1 block w-full text-gray-700"
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
                >
                    Upload Resume
                </button>
            </form>
            {message && <p className="mt-4 text-green-600">{message}</p>}
            {error && <p className="mt-4 text-red-600">{error}</p>}
        </div>
    );
}

export default ResumeUpload;