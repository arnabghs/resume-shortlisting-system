import { useState } from 'react';
import JobForm from './components/JobForm';
import ResumeUpload from './components/ResumeUpload';
import ShortlistView from './components/ShortlistView';

function App() {
    const [activeTab, setActiveTab] = useState('job');

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Resume Shortlisting System</h1>

            {/* Tabs for navigation */}
            <div className="flex space-x-4 mb-6">
                <button
                    className={`px-4 py-2 rounded ${activeTab === 'job' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                    onClick={() => setActiveTab('job')}
                >
                    Create Job
                </button>
                <button
                    className={`px-4 py-2 rounded ${activeTab === 'upload' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                    onClick={() => setActiveTab('upload')}
                >
                    Upload Resume
                </button>
                <button
                    className={`px-4 py-2 rounded ${activeTab === 'shortlist' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                    onClick={() => setActiveTab('shortlist')}
                >
                    View Shortlist
                </button>
            </div>

            {/* Render active component */}
            <div className="w-full max-w-2xl bg-white p-6 rounded-lg shadow">
                {activeTab === 'job' && <JobForm />}
                {activeTab === 'upload' && <ResumeUpload />}
                {activeTab === 'shortlist' && <ShortlistView />}
            </div>
        </div>
    );
}

export default App;