import json
import hashlib
import os
from constants import SAVE_DATA_FILE


class Instance(object):

    def __init__(self):
        self.data = []

    def collect(self, items):
        self.data += items
        self.save()

    def sort(self):
        self.data = sorted(self.data,
                           key=lambda s: s.get("title", s.get("code", "")))

    def save(self, save_path=None, data=None):
        if not save_path:
            save_path = SAVE_DATA_FILE
        if not data:
            data = {'data': self.data}
        self.sort()
        with open(save_path, 'w') as s:
            json.dump(data, s, ensure_ascii=False, indent=4)

    def load(self, file=SAVE_DATA_FILE):
        with open(file, 'r') as f:
            self.data = json.load(f).get('data')

    @staticmethod
    def hash(text):
        md5 = hashlib.md5()
        md5.update(text.encode('utf-8'))
        return md5.hexdigest()[:8]

    def build_diff_data(self):
        prev_file = os.popen('git show HEAD^:../data/syllabus.json').read()
        prev = json.loads(prev_file).get('data')
        for current_subject in self.data:
            code = current_subject.get('code')
            is_new = True
            for prev_subject in prev:
                if prev_subject.get('code') == code:
                    is_new = False
                    if prev_subject != current_subject:
                        print('update',prev_subject.get('title'))
                        self.diff(prev_subject,current_subject)

            if is_new:
                print('new',current_subject.get('title'))

    def diff(self, prev, current):
        for key in prev:
            prev_value = prev[key]
            current_value = current[key]
            if prev_value != current_value:
                if type(prev_value) == dict:
                    self.diff(prev_value,current_value)
                else:
                    print(f'\t- {prev_value}')
                    print(f'\t+ {current_value}')

    def build_search_data(self):
        teacher_list = []
        search_data = []

        for subject in self.data:
            origin_detail = subject['detail']

            detail_list = []
            detail_list.append(subject['title'])
            detail_list.append(origin_detail['day'])
            detail_list.append(origin_detail['target'])
            detail_list.append(origin_detail['purpose'])
            detail_list.append(origin_detail['teachingStyle'])
            detail_list.append(origin_detail['gradePolicy'])
            detail_list.append(origin_detail['finalTest'])
            detail_list.append(origin_detail['message'])
            detail_list.append(" ".join(origin_detail['keywords']))
            detail_list.append(" ".join(origin_detail['contents']))

            if (subject['teacher'] not in teacher_list):
                search_data.append({
                    'text': subject['teacher'],
                    'type': 'teacher',
                    'title': '教員',
                    'id': self.hash(f'teacher:{subject["teacher"]}'),
                })

                teacher_list.append(subject['teacher'])

            search_data.append({
                'text': " ".join(detail_list).strip(),
                'type': 'subject',
                'title': subject['title'],
                'id': subject['code']
            })

        self.save('../data/search.json',
                  {
                      'data': search_data
                  })


if __name__ == '__main__':
    db = Instance()
    db.load()
    #db.save()
    db.build_diff_data()
    # db.build_search_data()
