"""策略計算模組"""

class StrategyCalculator:
    INITIAL_WEIGHTS = {'core': 40, 'leverage': 30, 'cash': 30}
    DRAWDOWN_STEP = 5
    MAX_DRAWDOWN = -50
    MAX_LEVERAGE_WEIGHT = 50
    
    @staticmethod
    def calculate_beta(weights):
        """計算組合 Beta"""
        return (weights['core'] * 1.0 + 
                weights['leverage'] * 2.0 + 
                weights['cash'] * 0) / 100
    
    @staticmethod
    def calculate_drawdown(current_price, ath):
        """計算回撤"""
        if not current_price or not ath or ath == 0:
            return 0
        return ((current_price - ath) / ath) * 100
    
    @classmethod
    def check_adjustment_needed(cls, drawdown, current_weights):
        """檢查是否需要調整權重"""
        if drawdown > -5 or drawdown <= cls.MAX_DRAWDOWN:
            return {
                'required': False,
                'reason': '未觸發調整條件'
            }
        
        steps = int(abs(drawdown) // cls.DRAWDOWN_STEP)
        
        new_weights = {
            'core': cls.INITIAL_WEIGHTS['core'] - steps,
            'leverage': cls.INITIAL_WEIGHTS['leverage'] + (steps * 2),
            'cash': cls.INITIAL_WEIGHTS['cash'] - steps
        }
        
        if new_weights['leverage'] > cls.MAX_LEVERAGE_WEIGHT:
            return {
                'required': False,
                'reason': f"已達槓桿上限 {cls.MAX_LEVERAGE_WEIGHT}%"
            }
        
        return {
            'required': True,
            'drawdown': drawdown,
            'steps': steps,
            'old_weights': current_weights,
            'new_weights': new_weights,
            'beta': cls.calculate_beta(new_weights),
            'reason': f'槓桿回撤達 {drawdown:.1f}%，執行第 {steps} 階調整'
        }
