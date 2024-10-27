
import re
import os
import spacy
from pathlib import Path
import argparse

class DescriptorPath:
    def __init__(self):
        self.path = ''

    def __get__(self, instance, owner=None):
        return instance.__dict__.get('path', self.path)

    def __set__(self, instance, path):
        pattern = r"^[A-Z]:\\(?:[A-Za-z0-9_]+\\)*[A-Za-z0-9_]+$"
        if re.match(pattern, path) and os.path.isdir(path): #проверяем, что путь введен в нужном формате и он существует (хотя можно было только вторую проверку делать, наверное)
            instance.__dict__['path'] = path
        else:
            print('Введет некорректный путь к папке')

    def __delete__(self, instance):
        del instance.__dict__['path']






class CorpusCreator:    
    path = DescriptorPath()
    
    def __init__(self, folder, output_folder):
        self.path = folder
        self.output_folder = self.set_output_folder(output_folder)
        self.parser = spacy.load("en_core_web_sm")  

    def set_output_folder(self, folder_path):
        pattern = r"^[A-Z]:\\(?:[A-Za-z0-9_]+\\)*[A-Za-z0-9_]+$"
        try:
            re.match(pattern, folder_path)
            output_folder = Path(folder_path)
            output_folder.mkdir(exist_ok=True)  #Создаем папку, если она не существует
            return output_folder
        except ValueError:
            print('Некорректный формат пути')

    def openfile(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    yield os.path.join(root, file)  #Возвращаем полный пути к каждлму файлу

    def open_and_read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except (UnicodeDecodeError, FileNotFoundError) as e:
            self.log_error(file_path, e)
            return None

    def log_error(self, file_path, error):
        with open("errors.txt", "a") as log_file:
            log_file.write(f"{file_path}: {error}\n")

    def parse_text(self, text):
        doc = self.parser(text)
        conllu_data = []
        for sent in doc.sents:
            for token in sent:
                conllu_data.append(f"{token.i + 1}\t{token.text}\t{token.lemma_}\t{token.pos_}\t{token.tag_}\t{token.dep_}\t{token.head.i + 1 if token.head != token else 0}")
            conllu_data.append("")  #Пустая строка для разделения предложений
        conllu_data = "\n".join(conllu_data)
        return conllu_data

    def save_conllu(self, file_name, conllu_data):
        output_file_path = self.output_folder / f"{Path(file_name).stem}.conllu"
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(conllu_data)

    def process_files(self):
        for file_path in self.openfile():
            print(f"Обработка файла: {file_path}")
            text = self.open_and_read_file(file_path)
            if text: 
                conllu_data = self.parse_text(text)
                self.save_conllu(file_path, conllu_data)

    def run(self):
        self.process_files()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='txt to conllu')
    parser.add_argument('path', type=str, help='Введите путь к папке с исходными файлами')
    parser.add_argument('folder', type=str, help='Введите путь к папке для сохранения файлов')
    args = parser.parse_args()
    corpus_creator = CorpusCreator(args.path, args.folder)
    corpus_creator.run()
    

