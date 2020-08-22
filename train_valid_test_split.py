import os
from pathlib import Path
import shutil
import random
import click


@click.command()
@click.option("--input_dir_path", type=click.Path(exists=True), 
                  required=True,help='データセットが格納されたフォルダの絶対パス')
@click.option("--output_dir",type=click.Path(exists=False), help='出力先のディレクトリ名')
@click.option("--test_size", type=float, required=False, default=0.2)
@click.option("--valid_size", type=float, required=False,default=0.2)
@click.option("--shuffle", type=bool, required=False, default = True)
def train_valid_test_split(input_dir_path: str, output_dir: str, test_size: float = 0.2,valid_size: float=0.2,shuffle: bool=True):
    '''
    データをシャッフルして訓練・検証そしてテストの各ディレクトリに分割後、コピー保存する関数
    :params input_dir_path: オリジナルデータフォルダのパス その下に各クラスのフォルダがある
    :params output_dir: 分けたデータを格納するフォルダ名、
    　　　　　　　　　　　　オリジナルデータフォルダと同じ階層に作成する
    :params test_size: データセット分割時のtrain:testのtestデータの割合を指定　デフォルトは0.2
    :params valid_size: trainをさらに分割するときのtrain:validのvalidデータの割合を指定 デフォルトは0.2
    :params shuffle: shuffleするかどうかをbool値で指定 デフォルトはTrue。
    '''

    output_dir_path = Path(input_dir_path).parent.joinpath(output_dir).as_posix()
    os.makedirs(output_dir_path, exist_ok=True)
    # input_dir_path配下のオブジェクト名を取得
    obj_lists = os.listdir(input_dir_path)
    # クラス名のディレクトリを取得 
    class_dir_lists = [f for f in obj_lists if os.path.isdir(os.path.join(input_dir_path, f))]

    input_class_path_lists = [os.path.join(input_dir_path, p) for p in class_dir_lists]

    #train,valid,testのフォルダ作成
    dir_path_lists = []
    for d in ['train','valid','test']:
      dir_path = os.path.join(output_dir_path, d)
      os.makedirs(dir_path, exist_ok=True)
      dir_path_lists.append(dir_path)

    dir_path_dict= dict()
    for dir_path in dir_path_lists:#train, valid, testへのパスリスト
      class_dir_path_lists=[]
      for d in class_dir_lists: # クラス名のリスト
          class_dir_path = os.path.join(dir_path, d)
          os.makedirs(class_dir_path, exist_ok=True)
          class_dir_path_lists.append(class_dir_path)
      #train,valid,test配下のクラスディレクトパスのdict配列
      dir_path_dict[os.path.basename(dir_path)]=class_dir_path_lists
      
    #クラスごとにオリジナルデータをシャッフルしたものを上で作成したディレクトリにコピーする
    for i, path in enumerate(input_class_path_lists):
      print(path)
      try:
            file_lists = os.listdir(path)  # ファイルパスのリストを返す
            if shuffle:
              random.shuffle(file_lists)
              num_index = int(len(file_lists)*(1-test_size))
            else:
              num_index = int(len(file_lists)*(1-test_size))
            # testデータに分割
            for filename in file_lists[num_index:]:
                src = os.path.join(path, filename)
                dst = os.path.join(dir_path_dict['test'][i], filename)
                shutil.copyfile(src, dst)
            new_file_lists = file_lists[:num_index]
            if shuffle:
              random.shuffle(new_file_lists)
              num_index = int(len(new_file_lists)*(1-valid_size))
            else:
              num_index = int(len(new_file_lists)*(1-valid_size))
              
            # trainとvalidデータに分割
            for filename in new_file_lists[:num_index]:
                src = os.path.join(path, filename)
                dst = os.path.join(dir_path_dict['train'][i], filename)

                shutil.copyfile(src, dst)
            for filename in new_file_lists[num_index:]:
                src = os.path.join(path, filename)
                dst = os.path.join(dir_path_dict['valid'][i],filename)
                shutil.copyfile(src, dst)
            print(path + 'コピー完了')
      except: 
            print('There is no file in {} directory'.format(path.rsplit('/',1)[1]))

    print('complete')

if __name__ == '__main__':
    train_valid_test_split()
