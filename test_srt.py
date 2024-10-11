import unittest

from srt import fix_srt, Srt


def mock_srt(text: str) -> Srt:
    return Srt(0, 0, 0, text)


class TestSrt(unittest.TestCase):
    def test_fix_srt(self):
        expected_srt = [
            mock_srt("前面少字"),
            mock_srt("前面错字"),
            mock_srt("前面多字"),
            mock_srt("中间少字"),
            mock_srt("中间错字"),
            mock_srt("中间多字"),
            mock_srt("后面少字"),
            mock_srt("后面错字"),
            mock_srt("后面多字"),
            mock_srt("abc def ghi"),
            mock_srt("jkl mno pqr"),
            mock_srt("stu vwx yza"),
            mock_srt("bcd efg hij"),
            mock_srt("klm nop qrs"),
            # 预期中的行为, 因为
            # ["tuv", " ", "wxy", " ", "vvv", " " "zab"]
            # ["tuv", " ", "wxy", " ", "zab", " " "cde"]
            # 之间的比较结果是
            # ['  tuv', '   ', '  wxy', '   ', '- vvv', '+ zab', '   ', '- zab', '+ cde', '+  ', '+ fgh', '+  ', '+ ijk', '+  ', '+ lmn']
            # 这里难免将 cde 提前
            mock_srt("tuv wxy zab cde"),
            mock_srt("fgh ijk"),
            mock_srt("lmn opq rst"),
            mock_srt("uvw xyz abc"),
        ]
        srt = [
            mock_srt("面少字"),
            mock_srt("千面错字"),
            mock_srt("哦前面多字"),
            mock_srt("中少字"),
            mock_srt("中间错字"),
            mock_srt("中间多一字"),
            mock_srt("后面"),
            mock_srt("后面错子"),
            mock_srt("后面多字了"),
            mock_srt("def ghi"),
            mock_srt("xxx mno pqr"),
            mock_srt("vvv stu vwx yza"),
            mock_srt("bcd  hij"),
            mock_srt("klm xxx qrs"),
            mock_srt("tuv wxy vvv zab"),
            mock_srt("cde fgh"),
            mock_srt("lmn opq xxx"),
            mock_srt("uvw xyz abc vvv"),
        ]

        prompt = """前面少字,前面错字，前面多字。
    中间少字?中间错字!中间多字/
后面少字...后面错字？后面多字！abc def ghi. jkl mno pqr
stu vwx yza bcd efg hij klm nop qrs tuv wxy zab cde fgh ijk lmn opq rst. uvw xyz abc"""

        fix_srt(srt, prompt)
        self.assertListEqual(srt, expected_srt)

    def test_fix_srt_2(self):
        expected_srt = [
            mock_srt("Introduction to Fundamentals and Practices of Cross-Border E-commerce Live Streaming"),
            mock_srt("In today s hyper connected global economy cross border live streaming has swept the world"),
            mock_srt(
                "revolutionizing the landscape of how businesses forge connections with customers and promote sales"
            ),
            mock_srt(
                "to new heights This dynamic and rapidly growing industry is booming presenting unique opportunities"
            ),
            mock_srt(
                "for those who expertly navigate its intricacies Our course is specifically designed for ambitious"
            ),
            mock_srt("students worldwide who are eager to harness the immense potential of this burgeoning market"),
            mock_srt("and carve out their unique place in the digital landscape"),
        ]
        srt = [
            mock_srt(" Introduction to Fundamentals and Practices of Cross-Border E-Commerce Live Streaming"),
            mock_srt(" in today's hyperconnected global economy. Cross-border live streaming has swept the world,"),
            mock_srt(
                " revolutionizing the landscape of how businesses forge connections with customers and promote sales"
            ),
            mock_srt(
                " to new heights. This dynamic and rapidly growing industry is booming, presenting unique opportunities"
            ),
            mock_srt(
                " for those who expertly navigate its intricacies. Our course is specifically designed for ambitious"
            ),
            mock_srt(" students worldwide who are eager to harness the immense potential of this burdening market"),
            mock_srt(" and carve out their unique place in the digital landscape."),
        ]
        prompt = "Introduction to Fundamentals and Practices of Cross-Border E-commerce Live Streaming In today's hyper-connected global economy, cross-border live streaming has swept the world, revolutionizing the landscape of how businesses forge connections with customers and promote sales to new heights. This dynamic and rapidly growing industry is booming, presenting unique opportunities for those who expertly navigate its intricacies. Our course is specifically designed for ambitious students worldwide, who are eager to harness the immense potential of this burgeoning market and carve out their unique place in the digital landscape. "
        fix_srt(srt, prompt)
        self.assertListEqual(srt, expected_srt)


if __name__ == "__main__":
    unittest.main()
