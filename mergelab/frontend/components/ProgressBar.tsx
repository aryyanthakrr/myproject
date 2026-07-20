"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, Clock, AlertCircle, Download, MessageSquare, Cloud, Share2, Key, Hash } from "lucide-react";
import { mergeApi } from "@/lib/api";

interface ProgressBarProps {
  jobId: string | null;
  onComplete: (result: any) => void;
}

const STEPS = [
  { id: 'pending', name: 'Initializing...', icon: Clock },
  { id: 'downloading', name: 'Downloading models...', icon: Download },
  { id: 'merging', name: 'Merging layers...', icon: Cloud },
  { id: 'quantizing', name: 'Quantizing...', icon: Hash },
  { id: 'verifying', name: 'Verifying integrity...', icon: CheckCircle },
  { id: 'completed', name: 'Done!', icon: CheckCircle },
];

export default function ProgressBar({ jobId, onComplete }: ProgressBarProps) {
  const [status, setStatus] = useState<any>(null);
  const [testPrompt, setTestPrompt] = useState('');
  const [testResponse, setTestResponse] = useState<string | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    const pollStatus = async () => {
      try {
        const response = await mergeApi.status(jobId);
        setStatus(response.data);

        if (response.data.status === 'completed') {
          onComplete(response.data);
        } else if (response.data.status === 'failed') {
          onComplete(response.data);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [jobId, onComplete]);

  if (!jobId) {
    return (
      <div className="text-center py-12 text-gray-400">
        <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>Start a merge to see progress</p>
      </div>
    );
  }

  const currentStepIndex = STEPS.findIndex(s => s.id === status?.status);
  const isCompleted = status?.status === 'completed';
  const isFailed = status?.status === 'failed';

  const handleTest = async () => {
    if (!testPrompt || !jobId) return;
    
    setIsTesting(true);
    try {
      const response = await mergeApi.test(jobId, testPrompt);
      setTestResponse(response.data.response);
    } catch (error) {
      setTestResponse('Error testing model. Please try again.');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Steps */}
      <div className="space-y-4">
        {STEPS.map((step, index) => {
          const Icon = step.icon;
          const isActive = index === currentStepIndex;
          const isPast = index < currentStepIndex;
          
          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center space-x-3 p-3 rounded-lg ${
                isActive ? 'bg-accent/10 border border-accent' :
                isPast ? 'bg-green-500/10 border border-green-500' :
                'bg-card border border-white/10'
              }`}
            >
              <Icon className={`w-5 h-5 ${
                isActive ? 'text-accent' :
                isPast ? 'text-green-500' :
                'text-gray-500'
              }`} />
              <span className={`text-sm ${
                isActive ? 'text-white font-medium' :
                isPast ? 'text-green-500' :
                'text-gray-500'
              }`}>
                {step.name}
              </span>
              {isActive && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="ml-auto w-4 h-4 border-2 border-accent border-t-transparent rounded-full"
                />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Progress Bar */}
      <div className="relative">
        <div className="h-2 bg-card rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${status?.progress_percent || 0}%` }}
            className="h-full gradient-primary"
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-2">
          <span>{status?.progress_percent || 0}%</span>
          {status?.eta_seconds && (
            <span>ETA: ~{Math.round(status.eta_seconds / 60)}m</span>
          )}
        </div>
      </div>

      {/* Error Message */}
      {isFailed && (
        <div className="p-4 bg-red-500/10 border border-red-500 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <div>
              <p className="font-medium text-red-500">Merge Failed</p>
              <p className="text-sm text-gray-400">{status?.error_message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Test Chat (when completed) */}
      {isCompleted && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-accent" />
            <h3 className="font-semibold">Test Your Model</h3>
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              placeholder="Ask your merged model anything..."
              className="flex-1 bg-card border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent"
              onKeyDown={(e) => e.key === 'Enter' && handleTest()}
            />
            <button
              onClick={handleTest}
              disabled={isTesting || !testPrompt}
              className="px-4 py-2 bg-accent rounded-lg hover:bg-accent/80 disabled:opacity-50"
            >
              {isTesting ? '...' : 'Send'}
            </button>
          </div>
          
          {testResponse && (
            <div className="p-4 bg-card rounded-lg">
              <p className="text-sm text-gray-300">{testResponse}</p>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons (when completed) */}
      {isCompleted && (
        <div className="grid grid-cols-2 gap-3">
          <a
            href={mergeApi.download(jobId)}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-500/20 border border-green-500 rounded-lg hover:bg-green-500/30 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </a>
          
          <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-card border border-white/10 rounded-lg hover:border-accent transition-colors">
            <Cloud className="w-4 h-4" />
            <span>Deploy API</span>
          </button>
          
          <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-card border border-white/10 rounded-lg hover:border-accent transition-colors">
            <Share2 className="w-4 h-4" />
            <span>Push to HF</span>
          </button>
          
          <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-card border border-white/10 rounded-lg hover:border-accent transition-colors">
            <Key className="w-4 h-4" />
            <span>Share Config</span>
          </button>
        </div>
      )}
    </div>
  );
}
