import {useState} from 'react';
import axios from 'axios';

function JobForm() {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        required_skills: '',
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        try {
            const response = await axios.post('http://localhost:8000/api/jobs', formData, {
                headers: {'Content-Type': 'multipart/form-data'},
            });
            setMessage(`Job created successfully! Job ID: ${response.data.id}`);
            setFormData({title: '', description: '', required_skills: ''});
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create job');
        }
    };

    return (
        <div>
            <h2 className="text-xl font-semibold mb-4">Create Job</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Job Title</label>
                    <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        rows="4"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Required Skills</label>
                    <input
                        type="text"
                        name="required_skills"
                        value={formData.required_skills}
                        onChange={handleChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        placeholder="e.g., Python, SQL, FastAPI"
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
                >
                    Create Job
                </button>
            </form>
            {message && <p className="mt-4 text-green-600">{message}</p>}
            {error && <p className="mt-4 text-red-600">{error}</p>}
        </div>
    );
}

export default JobForm;
