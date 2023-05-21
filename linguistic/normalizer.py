"""
‫با توجه به استفاده این فایل دو تا تابع داره که یکی برای نرمال کردن پرس‌وجو است و دیگری برای نرمال کردن متن
"""
import pandas as pd
import re
import os

charTable = pd.read_csv(os.path.abspath('linguistic/data/chars.csv'), delimiter=',')
SW = pd.read_csv(os.path.abspath('linguistic/data/specialWords.csv'), delimiter=',')


def maketrans(A, B): return dict((ord(a), b) for a, b in zip(A, B))


def compile_patterns(patterns): return [
    (re.compile(pattern), repl) for pattern, repl in patterns]


# ‫این کلاس تمامی به هنجارسازی های گفته شده در readme را انجام می‌دهد
class Normalizer:
    '''
    # Note:
        - If using half_space_to_space >> half_space must be True
    # Params:
        ## remove_extra_spaces: (if True > strip query)
        ## persian_numbers: (True > Convert persian numbers to english style)
        ## unicode: (True > Convert words in chars.csv to a normal style)
        ## word_refine: (True > Refine some special words to a normal style)
        ## affix_spacing: (True > Normalize space which used for "date, clock, fractional" format)
        ## persian_style: (True > Refine some persian styles (More comments are in code))
        ## punctuation_spacing: (True > Refine the pattern which includes punctuations and spaces inside each other)
        ## half_space: (True > Put half space betweet some persian words like "می توان", False > join this kind of words together)
        ## half_space_to_space: (True > Convert half space to space(attention to note))
        ## remove_emoji: (True > Remove emojies)
        ## remove_diacritics: (True > Remove "FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA,KASRA,MADHE,HAMZE")
        ## word_number_separation: (True > Separate word from numbers)
        ## remove_punctuation: (True > Remove puctuations)
        ## remove_repeated_word: (True > Remove words which are repeated continuously)
    '''
    def __init__(
            self,
            remove_extra_spaces=True,
            persian_numbers=True,
            unicode=True,
            word_refine=True,
            affix_spacing=True,
            persian_style=True,
            punctuation_spacing=True,
            half_space=True,
            half_space_to_space = False,
            remove_emoji=True,
            remove_diacritics=True,
            word_number_separation=True,
            remove_punctuation=True,
            remove_repeated_word=True):
        self._punctuation_spacing = punctuation_spacing
        self._remove_emoji = remove_emoji
        self._word_number_separation = word_number_separation
        self._affix_spacing = affix_spacing
        self._half_space = half_space
        self._half_space_to_space = half_space_to_space
        translation_src, translation_dst = "", ""
        # ‫تبدیل اعدادفارسی  به انگلیسی
        if persian_numbers:
            translation_src += '۰۱۲۳۴۵۶۷۸۹٪'
            translation_dst += '0123456789%'
        if unicode:
            translation_src += ' ىكي“”'
            translation_dst += ' یکی""'
            unicode_chars = ''.join(list(charTable['unicode']))
            translation_src += unicode_chars
            original_chars = ''.join(list(charTable['orginal']))
            translation_dst += original_chars
        self.translations = maketrans(translation_src, translation_dst)
        self.character_refinement_patterns = []
        self.affix_spacing_patterns = []

        if remove_diacritics:
            self.character_refinement_patterns.append(
                ('[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u007e\u0621\u0654]', ''),
                # remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA,KASRA,MADHE,HAMZE
            )
        if word_refine:
            self.character_refinement_patterns.extend(
                list(zip(SW['before'], SW['after'])))

        if word_number_separation:
            self.character_refinement_patterns.extend([
                (r'([^\d+])([\d+])', r'\1 \2'),
                (r'([\d+])([^\d+])', r'\1 \2'),
                (r'([\d+])\s([%])', r'\1\2'),
                (r'([%])([^\d+])', r'\1 \2')
            ])
        if persian_style:
            self.character_refinement_patterns.extend([
                ('"([^\n"]+)"', r'«\1»'),  # replace quotation with gyoome
                (r'\.\.\.', '…'),  # replace 3 dots with one char '…'
                (r'([^0-9])(\1{2,})', r'\1'),  # remove repeating of a chars (except numbers)
                (r'[ـ\r]', ''),  # remove keshide, carriage returns
                (r'([\u0600-\u06FF])([a-zA-Z])', r'\1 \2'),  # put space between persian and english chars
                (r'([a-zA-Z])([\u0600-\u06FF])', r'\1 \2')  # put space between persian and english chars
            ])

        if remove_punctuation:
            self.character_refinement_patterns.extend([
                (r'[؟!،,…/#_!"$&()*,;<=>?^`{|}~–?-]', " "),
                (r"[']", " "),
            ])
        if remove_extra_spaces:
            self.character_refinement_patterns.extend([
                (r' +', ' '),  # remove extra spaces
                (r'\n\n+', '\n'),  # remove extra newlines
                (r'\r\n+', '\r\n'),  # remove extra newlines
                (r'\s+\n', '\n'),  # end of the paragraph delete space before \n
                (r'\n\s+', '\n'),  # end of the paragraph delete space before \n
            ])
        if remove_repeated_word:
            self.character_refinement_patterns.extend([
                (r'\b(\w+)( \1\b)+', r'\1')
            ])
        self.character_refinement_patterns = compile_patterns(
            self.character_refinement_patterns)

        punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'\[\(\{'
        if punctuation_spacing:
            self.punctuation_spacing_patterns = compile_patterns([
                # remove space before and after quotation
                ('" ([^\n"]+) "', r'"\1"'),
                (' ([' + punc_after + '])', r'\1'),  # remove space before
                ('([' + punc_before + ']) ', r'\1'),  # remove space after
                ('([' + punc_after[:3] + '])([^ ' + punc_after + '\\d0123456789])', r'\1 \2'),
                # put space after . and :
                ('([' + punc_after[3:] + '])([^ ' + punc_after + '])', r'\1 \2'),  # put space after
                ('([^ ' + punc_before + '])([' + punc_before + '])', r'\1 \2'),  # put space before
            ])

        if affix_spacing:
            self.affix_spacing_patterns.extend([
                (r'([^ ]ه) ی ', r'\1‌ی '),  # fix ی space
                (r'([\d+])\s\.\s([\d+])', r'\1.\2'),  # for fractional numbers
                (r'([\d+])\s\:\s([\d+])', r'\1:\2'),  # for clock format
                (r'([\d+])\s\/\s([\d+])', r'\1/\2'),  # for date format
                (r'([\d+])\s\-\s([\d+])', r'\1-\2'),  # for date format
                (r'([\d+])/([\d+])', r'\1.\2'),  # for fractional numbers
                (r'([\d+])/([\d+])', r'\1.\2'),
                (r'([a-zA-Z0-9])[.]\s([a-zA-Z0-9])', r'\1.\2'),  # gmail and website format
                (r'([^ ]ه) (ا(م|یم|ش|ند|ی|ید|ت))(?=[ \n' + punc_after + ']|$)', r'\1‌\2')
            ])
        if half_space:
            self.affix_spacing_patterns.extend([
                (r'(^| )(ن?می) ', r'\1\2‌'),  # put zwnj after می, نمی
                (
                    r'(?<=[^\n\d ' + punc_after + punc_before + ']{2}) (تر(ین?)?|گری?|های?)(?=[ \n' + punc_after + punc_before + ']|$)',
                    r'‌\1'),  # put zwnj before تر, تری, ترین, گر, گری, ها, های
                # join ام, ایم, اش, اند, ای, اید, ات
            ])
        else:
            self.affix_spacing_patterns.extend([
                (r'(^| )(ن?می) ', r'\1\2'),  # put zwnj after می, نمی
                (
                    r'(?<=[^\n\d ' + punc_after + punc_before + ']{2}) (تر(ین?)?|گری?|های?)(?=[ \n' + punc_after + punc_before + ']|$)',
                    r'\1'),  # put zwnj before تر, تری, ترین, گر, گری, ها, های
                (r'‌', ''),
            ])
        if half_space_to_space:
            self.affix_spacing_patterns.extend([
                (r'‌', ' ')
            ])
        self.affix_spacing_patterns = compile_patterns(
            self.affix_spacing_patterns)



    def character_refinement(self, text):
        text = text.translate(self.translations)
        for pattern, repl in self.character_refinement_patterns:
            text = pattern.sub(repl, text)
        return text



    # ‫حذف اموجی‌ها
    @staticmethod
    def remove_emoji(text):
        regrex_pattern = re.compile(pattern="["
                                            u"\U0001F600-\U0001F64F"  # emoticons
                                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                            u"\U00002500-\U00002BEF"  # chinese char
                                            u"\U00002702-\U000027B0"
                                            u"\U00002702-\U000027B0"
                                            u"\U000024C2-\U0001F251"
                                            u"\U0001f926-\U0001f937"
                                            u"\U00010000-\U0010ffff"
                                            u"\u2640-\u2642"
                                            u"\u2600-\u2B55"
                                            u"\u200d"
                                            u"\u23cf"
                                            u"\u23e9"
                                            u"\u231a"
                                            u"\ufe0f"  # dingbats
                                            u"\u3030"
                                            u"\u066c"
                                            u"\u2022"
                                            u"\u00a1"
                                            u"\u00b9"
                                            u"\u00ae"
                                            "]+", flags=re.UNICODE)
        return regrex_pattern.sub(r' ', text)



    # ‫این تابع برای قرار دادن space بعد از punctuation هاست
    def punctuation_spacing(self, text):
        for pattern, repl in self.punctuation_spacing_patterns:
            text = pattern.sub(repl, text)
        return text



    # این تابع برای اصلاح نیم‌فاصله‌هاست
    def affix_spacing(self, text):
        for pattern, repl in self.affix_spacing_patterns:
            text = pattern.sub(repl, text)
        return text



    # تابع اصلی برای نرمال کردن متن
    def normalize_text(self, text):
        text = text.lower()
        if self._remove_emoji:
            text = self.remove_emoji(text).strip()
        text = self.character_refinement(text)
        if self._punctuation_spacing:
            text = self.punctuation_spacing(text)
        if self._affix_spacing:
            text = self.affix_spacing(text)
        return text.strip()
