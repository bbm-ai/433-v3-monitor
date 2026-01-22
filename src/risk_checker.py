"""風險檢查模組"""

class RiskChecker:
    MAX_PLEDGE_RATIO = 20
    MIN_MAINTENANCE_RATE = 220
    
    @classmethod
    def check_risks(cls, portfolio):
        """檢查所有風險紅線"""
        risks = []
        
        # 質押比例檢查
        pledge_ratio = (portfolio['pledge_amount'] / portfolio['total_value']) * 100
        if pledge_ratio > cls.MAX_PLEDGE_RATIO:
            risks.append({
                'level': 'critical',
                'type': 'PLEDGE_RATIO',
                'message': f'質押比例 {pledge_ratio:.1f}% 超過 {cls.MAX_PLEDGE_RATIO}% 紅線',
                'action': '停止所有加碼動作'
            })
        
        # 維持率檢查
        if portfolio['maintenance_rate'] < cls.MIN_MAINTENANCE_RATE:
            risks.append({
                'level': 'critical',
                'type': 'MAINTENANCE_RATE',
                'message': f'維持率 {portfolio["maintenance_rate"]}% 低於 {cls.MIN_MAINTENANCE_RATE}% 紅線',
                'action': '進入保守模式'
            })
        
        # 現金覆蓋檢查
        if portfolio['cash_value'] < portfolio['pledge_amount']:
            risks.append({
                'level': 'warning',
                'type': 'CASH_COVERAGE',
                'message': '現金部位不足以覆蓋質押借款',
                'action': '建議增加現金部位'
            })
        
        return risks
