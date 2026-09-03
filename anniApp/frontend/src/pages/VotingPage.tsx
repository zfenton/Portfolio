import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Heart } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { votingApi, type Activity } from '../lib/api';

export default function VotingPage() {
  const { activityNumber } = useParams<{ activityNumber: string }>();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const currentIndex = parseInt(activityNumber || '1') - 1;
  const currentActivity = activities[currentIndex];
  const totalActivities = activities.length;

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/');
      return;
    }

    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      const data = await votingApi.getActivities();
      setActivities(data);
    } catch (error) {
      console.error('Error fetching activities:', error);
      alert('Failed to load activities. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (selectedOption === null) return;

    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/');
      return;
    }

    setSubmitting(true);
    try {
      await votingApi.submitVote(parseInt(userId), {
        activity_id: currentActivity.id,
        option_id: selectedOption,
      });

      if (currentIndex < totalActivities - 1) {
        navigate(`/vote/${currentIndex + 2}`);
        setSelectedOption(null);
      } else {
        navigate('/message');
      }
    } catch (error) {
      console.error('Error submitting vote:', error);
      alert('Failed to submit vote. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    if (currentIndex > 0) {
      navigate(`/vote/${currentIndex}`);
      setSelectedOption(null);
    } else {
      navigate('/');
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

  if (!currentActivity) {
    return <div>Activity not found</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.4 }}
        >
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">
                Question {currentIndex + 1} of {totalActivities}
              </span>
              <span className="text-sm font-medium text-pink-600">
                {Math.round(((currentIndex + 1) / totalActivities) * 100)}% Complete
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="celebration-gradient h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{
                  width: `${((currentIndex + 1) / totalActivities) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          <Card className="border-2 border-purple-200 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl">{currentActivity.question}</CardTitle>
              <CardDescription>Choose the option you think would be perfect!</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <RadioGroup value={selectedOption?.toString()} onValueChange={(value) => setSelectedOption(parseInt(value))}>
                <AnimatePresence>
                  {currentActivity.options
                    .sort((a, b) => a.order - b.order)
                    .map((option, index) => (
                      <motion.div
                        key={option.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <div
                          className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer hover:border-pink-300 hover:bg-pink-50 ${
                            selectedOption === option.id
                              ? 'border-pink-500 bg-pink-50'
                              : 'border-gray-200'
                          }`}
                          onClick={() => setSelectedOption(option.id)}
                        >
                          <RadioGroupItem value={option.id.toString()} id={`option-${option.id}`} />
                          <Label
                            htmlFor={`option-${option.id}`}
                            className="flex-1 cursor-pointer text-base"
                          >
                            {option.option_text}
                          </Label>
                        </div>
                      </motion.div>
                    ))}
                </AnimatePresence>
              </RadioGroup>

              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="flex-1"
                  disabled={submitting}
                >
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
                <Button
                  onClick={handleNext}
                  className="flex-1 celebration-gradient text-white"
                  disabled={selectedOption === null || submitting}
                >
                  {submitting ? 'Submitting...' : currentIndex < totalActivities - 1 ? 'Next' : 'Continue'}
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
