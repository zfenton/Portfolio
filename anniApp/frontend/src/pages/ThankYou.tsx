import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Heart, Sparkles, PartyPopper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

export default function ThankYou() {
  useEffect(() => {
    const confettiColors = ['#ec4899', '#a855f7', '#eab308', '#f97316'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
      createConfetti(confettiColors[Math.floor(Math.random() * confettiColors.length)]);
    }
  }, []);

  const createConfetti = (color: string) => {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = color;
    confetti.style.left = Math.random() * 100 + '%';
    confetti.style.top = '-10px';
    confetti.style.opacity = '1';
    confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
    confetti.style.pointerEvents = 'none';
    confetti.style.zIndex = '9999';
    document.body.appendChild(confetti);

    let top = -10;
    let left = parseFloat(confetti.style.left);
    const drift = (Math.random() - 0.5) * 2;

    const fall = setInterval(() => {
      top += 2;
      left += drift;
      confetti.style.top = top + 'px';
      confetti.style.left = left + '%';
      confetti.style.opacity = (1 - top / window.innerHeight).toString();

      if (top > window.innerHeight) {
        clearInterval(fall);
        confetti.remove();
      }
    }, 20);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, type: 'spring' }}
        className="w-full max-w-md"
      >
        <Card className="border-2 border-pink-300 shadow-2xl text-center">
          <CardHeader className="space-y-6 pb-8">
            <motion.div
              animate={{
                rotate: [0, 15, -15, 0],
                scale: [1, 1.2, 1.2, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 1,
              }}
              className="flex justify-center"
            >
              <div className="celebration-gradient p-6 rounded-full inline-block">
                <PartyPopper className="w-16 h-16 text-white" />
              </div>
            </motion.div>
            <div>
              <CardTitle className="text-4xl font-bold celebration-gradient bg-clip-text text-transparent mb-4">
                Thank You!
              </CardTitle>
              <p className="text-lg text-muted-foreground">
                Your votes and wishes have been recorded
              </p>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 pb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-center gap-2 text-pink-600">
                <Heart className="w-5 h-5" fill="currentColor" />
                <Sparkles className="w-5 h-5" fill="currentColor" />
                <Heart className="w-5 h-5" fill="currentColor" />
              </div>
              <p className="text-base text-gray-700">
                Your votes will help create an unforgettable memory for our 18th anniversary celebration!
              </p>
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-muted-foreground">
                  Thank you for being part of our journey
                </p>
              </div>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
