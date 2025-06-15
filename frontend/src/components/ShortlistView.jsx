import { useState } from 'react';
import axios from 'axios';

function ShortlistView() {
    const [jobId, setJobId] = useState('');
    const [limit, setLimit] = useState('');
    const [candidates, setCandidates] = useState([]);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setCandidates([]);
        try {
            const response = await axios.get('http://localhost:8000/api/shortlist', {
                params: { job_id: jobId, limit: limit || 0 },
            });
            setCandidates(response.data.results);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch candidates');
        }
    };

    return (
        <div>
            <h2 className="text-xl font-semibold mb-4">View Shortlisted Candidates</h2>
            <form onSubmit={handleSubmit} className="space-y-4 mb-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Job ID</label>
                    <input
                        type="number"
                        value={jobId}
                        onChange={(e) => setJobId(e.target.value)}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Limit (Optional)</label>
                    <input
                        type="number"
                        value={limit}
                        onChange={(e) => setLimit(e.target.value)}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2"
                        placeholder="e.g., 5"
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
                >
                    Fetch Candidates
                </button>
            </form>
            {error && <p className="mb-4 text-red-600">{error}</p>}
            {candidates.length > 0 && (
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border border-gray-200">
                        <thead>
                        <tr>
                            <th className="py-2 px-4 border-b text-left">ID</th>
                            <th className="py-2 px-4 border-b text-left">Name</th>
                            <th className="py-2 px-4 border-b text-left">Email</th>
                            <th className="py-2 px-4 border-b text-left">Score</th>
                        </tr>
                        </thead>
                        <tbody>
                        {candidates.map((candidate) => (
                            <tr key={candidate.id}>
                                <td className="py-2 px-4 border-b">{candidate.id}</td>
                                <td className="py-2 px-4 border-b">{candidate.name}</td>
                                <td className="py-2 px-4 border-b">{candidate.email}</td>
                                <td className="py-2 px-4 border-b">{candidate.score.toFixed(2)}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default ShortlistView;