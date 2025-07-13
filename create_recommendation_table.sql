-- 创建推荐记录表
CREATE TABLE IF NOT EXISTS `number8_recommendations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qishu` int(11) NOT NULL,
  `recommend_numbers` varchar(128) NOT NULL,
  `strategy` varchar(128) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `extra` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_qishu` (`qishu`),
  KEY `idx_qishu` (`qishu`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='该表记录每5期的推荐8码';

-- 插入一些示例数据（可选）
-- INSERT INTO number8_recommendations (qishu, recommend_numbers, strategy, extra) VALUES 
-- (2025001, '12,23,34,45,56,67,78,89', '第七码高频推荐', '最新系统推荐8码'),
-- (2025005, '11,22,33,44,55,66,77,88', '第七码高频推荐', '最新系统推荐8码'),
-- (2025010, '10,20,30,40,50,60,70,80', '第七码高频推荐', '最新系统推荐8码'); 