import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { userApi } from '../lib/api';

export default function Welcome() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      const user = await userApi.register(name.trim());
      localStorage.setItem('userId', user.id.toString());
      localStorage.setItem('userName', user.name);
      navigate('/vote/1');
    } catch (error) {
      console.error('Error registering user:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        <Card className="border-2 border-pink-200 shadow-xl card-shimmer overflow-hidden">
          <CardHeader className="text-center space-y-4 pb-4">
            <motion.div
              animate={{
                rotate: [0, 10, -10, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
              className="flex justify-center"
            >
              <div className="celebration-gradient p-4 rounded-full inline-block">
                <Heart className="w-12 h-12 text-white" fill="white" />
              </div>
            </motion.div>
            <div>
              <CardTitle className="text-3xl font-bold celebration-gradient bg-clip-text text-transparent">
                Rachelle and Zach are celebrating 18 years of love!!!
              </CardTitle>
              <CardDescription className="text-base mt-2">
                <p>
                  And what is the most important thing that happens at 18 years?
                </p>
                <p>
                  <span>You get to VOTE!!!</span>
                </p>
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground justify-center">
              <Sparkles className="w-4 h-4 text-yellow-500" />
              <span>Your votes will help plan the perfect anniversary celebration</span>
              <Sparkles className="w-4 h-4 text-yellow-500" />
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Enter your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="text-center text-lg h-12 border-2 focus:border-pink-400"
                  disabled={loading}
                  required
                />
              </div>
              <Button
                type="submit"
                className="w-full celebration-gradient text-white text-lg h-12 font-semibold shadow-lg hover:shadow-xl transition-all"
                disabled={loading || !name.trim()}
              >
                {loading ? 'Starting...' : "Let's Celebrate!"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
