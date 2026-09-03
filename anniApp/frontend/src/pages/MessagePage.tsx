import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Send, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { messageApi } from '../lib/api';

export default function MessagePage() {
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/');
      return;
    }

    setSubmitting(true);
    try {
      await messageApi.submitMessage(parseInt(userId), {
        message_text: message.trim(),
      });
      navigate('/thank-you');
    } catch (error) {
      console.error('Error submitting message:', error);
      alert('Failed to submit message. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <Card className="border-2 border-yellow-200 shadow-xl">
          <CardHeader className="text-center">
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 2,
              }}
              className="flex justify-center mb-4"
            >
              <div className="celebration-gradient p-4 rounded-full inline-block">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
            </motion.div>
            <CardTitle className="text-3xl">Share Your Wishes</CardTitle>
            <CardDescription className="text-base">
              Leave a special message to celebrate this beautiful milestone
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Share your congratulations, favorite memories, or wishes for the happy couple..."
                  className="w-full min-h-[200px] p-4 rounded-lg border-2 border-gray-200 focus:border-pink-400 focus:outline-none resize-none text-base"
                  disabled={submitting}
                  required
                />
                <p className="text-sm text-muted-foreground text-right">
                  {message.length} characters
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(-1)}
                  className="flex-1"
                  disabled={submitting}
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  className="flex-1 celebration-gradient text-white text-lg h-12 font-semibold"
                  disabled={submitting || !message.trim()}
                >
                  {submitting ? (
                    'Sending...'
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      Send Wishes
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
