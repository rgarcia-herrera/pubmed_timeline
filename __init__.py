from pattern.vector import Document
import time
import datetime


uninteresting_terms = ['Humans', 'Male', 'Female', ]


class Year:

    refs = {}

    def __init__(self, year):
        self.year = year

    def add_ref(self, pmid, kw_fq):
        self.refs[pmid] = kw_fq

    def get_keywords(self):
        kw = set()
        for pmid in self.refs:
            for w in self.refs[pmid].keys():
                kw.add(w)
        return kw

    def get_frequencies_for_kw(self, kw):
        freqs = list()
        for pmid in self.refs:
            freqs.append(self.refs[pmid].get(kw, 0))
        return freqs

    def get_normalized_kw_fq(self):
        kw_fq = dict()
        for kw in self.get_keywords():
            kw_fq[kw] = sum(self.get_frequencies_for_kw(kw)) \
                        / float(len(self.get_keywords()))
        return kw_fq


class Citation:
    def __init__(self, medline_record):

        self.record = medline_record

        # get citation date
        assert 'EDAT' in medline_record.keys()
        try:
            conv = time.strptime(medline_record['EDAT'], "%Y/%m/%d %H:%M")
            self.date = datetime.datetime(*conv[:6])  # entrez date
        except ValueError:
            conv = time.strptime(medline_record['EDAT'], "%Y/%m/%d")
            self.date = datetime.datetime(*conv[:6])  # entrez date

    def get_meshterms(self):
        if 'MH' in self.record:
            # grab mesh terms
            mh = Document(self.record['MH'])
        elif 'OT' in self.record:
            mh = Document(self.record['OT'])
        else:
            return {}

        main_terms = set()
        other_terms = set()
        for term in mh:
            words = term.split('/')
            for w in words:
                if w not in uninteresting_terms:
                    if '*' in w:
                        main_terms.add(w.replace('*', ''))
                    else:
                        other_terms.add(w)
        total_terms = float(len(main_terms) + len(other_terms))
        main_terms_fq = dict()
        for term in main_terms:
            main_terms_fq[term] = (1 / total_terms) * 2
        other_terms_fq = dict()
        for term in other_terms:
            other_terms_fq[term] = 1 / total_terms

        # importance adjusted frequency total
        f = sum(main_terms_fq.values()) + sum(other_terms_fq.values())

        terms = dict()
        for term in main_terms:
            terms[term] = main_terms_fq[term] / f
        for term in other_terms:
            terms[term] = other_terms_fq[term] / f

        return terms

    def get_keywords(self):
        """ use pattern.Document to grab keywords from title or abstract """
        # if 'OT' not in self.record and 'MH' not in r:
        d = Document(self.record.get('TI',
                                     self.record.get('AB')))
        kw = dict()
        for w in d.keywords():
            kw[w[1]] = w[0]

        return kw
