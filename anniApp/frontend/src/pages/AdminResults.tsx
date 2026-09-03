import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Heart, MessageSquare, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { adminApi, type ActivityResult, type MessageResponse } from '../lib/api';

export default function AdminResults() {
  const [results, setResults] = useState<ActivityResult[]>([]);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showMessages, setShowMessages] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const [resultsData, messagesData] = await Promise.all([
        adminApi.getResults(),
        adminApi.getMessages(),
      ]);
      setResults(resultsData);
      setMessages(messagesData);
    } catch (error) {
      console.error('Error fetching results:', error);
      alert('Failed to load results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < results.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowMessages(true);
    }
  };

  const handleBack = () => {
    if (showMessages) {
      setShowMessages(false);
      setCurrentIndex(results.length - 1);
    } else if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Heart className="w-12 h-12 text-pink-500" />
        </motion.div>
      </div>
    );
  }

  if (showMessages) {
    return (
      <div className="min-h-screen p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 text-center"
          >
            <h1 className="text-4xl font-bold celebration-gradient bg-clip-text text-transparent mb-2">
              Messages of Love
            </h1>
            <p className="text-muted-foreground">Wishes from your loved ones</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            <AnimatePresence>
              {messages.map((msg, index) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="h-full border-2 border-pink-100 hover:border-pink-300 transition-all hover:shadow-lg">
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-pink-500" />
                        <CardTitle className="text-lg">Anonymous</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 whitespace-pre-wrap">{msg.message_text}</p>
                      <p className="text-xs text-muted-foreground mt-4">
                        {new Date(msg.created_at).toLocaleDateString()}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <div className="flex justify-center">
            <Button
              variant="outline"
              onClick={handleBack}
              className="px-8"
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Back to Results
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const currentResult = results[currentIndex];

  if (!currentResult) {
    return <div>No results available</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="mb-6 text-center">
            <h1 className="text-4xl font-bold celebration-gradient bg-clip-text text-transparent mb-2">
              Anniversary Celebration Results
            </h1>
            <p className="text-muted-foreground">
              Activity {currentIndex + 1} of {results.length}
            </p>
          </div>

          <Card className="border-2 border-purple-200 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl">{currentResult.question}</CardTitle>
              <CardDescription className="flex items-center gap-2 text-base">
                <TrendingUp className="w-4 h-4" />
                Total votes: {currentResult.total_votes}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <AnimatePresence mode="wait">
                {currentResult.vote_counts.map((voteCount, index) => {
                  const percentage = currentResult.total_votes > 0
                    ? Math.round((voteCount.vote_count / currentResult.total_votes) * 100)
                    : 0;

                  return (
                    <motion.div
                      key={voteCount.option_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="space-y-2"
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-700">{voteCount.option_text}</span>
                        <span className="text-sm font-bold text-pink-600">
                          {voteCount.vote_count} votes ({percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-8 overflow-hidden">
                        <motion.div
                          className="celebration-gradient h-8 rounded-full flex items-center justify-end px-3"
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 1, delay: index * 0.1 }}
                        >
                          {percentage > 15 && (
                            <span className="text-white text-sm font-semibold">
                              {percentage}%
                            </span>
                          )}
                        </motion.div>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>

              <div className="flex gap-3 pt-6">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="flex-1"
                  disabled={currentIndex === 0}
                >
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Previous
                </Button>
                <Button
                  onClick={handleNext}
                  className="flex-1 celebration-gradient text-white"
                >
                  {currentIndex < results.length - 1 ? 'Next' : 'View Messages'}
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
