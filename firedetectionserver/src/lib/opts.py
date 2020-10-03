from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import sys
import read_classes

class opts(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        # basic experiment setting
        self.task = 'objdet'
        self.dataset = 'objdet'
        self.exp_id = 'default'
        self.debug = 1
        self.demo = ''
        self.load_model = '../models/model_best.pth'
        self.resume = False
        # system
        self.gpus = '0'
        self.num_workers = 8
        self.not_cuda_benchmark = False
        self.seed = 317
        # log
        self.print_iter = 0
        self.hide_data_time = False
        self.save_all = False
        self.metric = 'loss'
        self.vis_thresh = 0.3
        self.debugger_theme = 'white'

        # model
        self.arch = 'dla_34'
        self.head_conv = -1
        self.down_ratio = 4
        # input
        self.input_res = -1
        self.input_h = -1
        self.input_w = -1
        # train
        self.lr = 1.25e-4
        self.lr_step = '90,120'
        self.num_epochs = 140
        self.batch_size = 32
        self.master_batch_size = -1
        self.num_iters = -1
        self.val_intervals = 5
        self.trainval = False
        # test
        self.flip_test = False
        self.test_scales = '1'
        self.nms = False
        self.K = 100
        self.not_prefetch_test = False
        self.fix_res = False
        self.keep_res = False

        # dataset
        self.not_rand_crop = False
        self.shift = 0.1
        self.scale = 0.4
        self.rotate = 0
        self.flip = 0.5
        self.no_color_aug = False

        # loss
        self.mse_loss = False
        # ctdet
        self.reg_loss = 'l1'
        self.hm_weight = 1
        self.off_weight = 1
        self.wh_weight = 0.1

        # task
        # ctdet
        self.norm_wh = False
        self.dense_wh = False
        self.cat_spec_wh = False
        self.not_reg_offset = False

    def parse(self, args=''):
        # if args == '':
        #     opt = self.parser.parse_args()
        # else:
        #     opt = self.parser.parse_args(args)
        opt = opts()

        opt.gpus_str = opt.gpus
        opt.gpus = [int(gpu) for gpu in opt.gpus.split(',')]
        opt.gpus = [i for i in range(
            len(opt.gpus))] if opt.gpus[0] >= 0 else [-1]
        opt.lr_step = [int(i) for i in opt.lr_step.split(',')]
        opt.test_scales = [float(i) for i in opt.test_scales.split(',')]

        opt.fix_res = not opt.keep_res
        print('Fix size testing.' if opt.fix_res else 'Keep resolution testing.')
        opt.reg_offset = True
        opt.reg_bbox = True
        opt.hm_hp = True
        opt.reg_hp_offset = True

        if opt.head_conv == -1:  # init default head_conv
            opt.head_conv = 256 if 'dla' in opt.arch else 64
        opt.pad = 127 if 'hourglass' in opt.arch else 31
        opt.num_stacks = 2 if opt.arch == 'hourglass' else 1

        if opt.trainval:
            opt.val_intervals = 100000000

        if opt.debug > 0:
            opt.num_workers = 0
            opt.batch_size = 1
            opt.gpus = [opt.gpus[0]]
            opt.master_batch_size = -1

        if opt.master_batch_size == -1:
            opt.master_batch_size = opt.batch_size // len(opt.gpus)
        rest_batch_size = (opt.batch_size - opt.master_batch_size)
        opt.chunk_sizes = [opt.master_batch_size]
        for i in range(len(opt.gpus) - 1):
            slave_chunk_size = rest_batch_size // (len(opt.gpus) - 1)
            if i < rest_batch_size % (len(opt.gpus) - 1):
                slave_chunk_size += 1
            opt.chunk_sizes.append(slave_chunk_size)
        print('training chunk_sizes:', opt.chunk_sizes)

        opt.root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        opt.data_dir = os.path.join(opt.root_dir, 'data')
        opt.exp_dir = os.path.join(opt.root_dir, 'exp', opt.task)
        opt.save_dir = os.path.join(opt.exp_dir, opt.exp_id)
        opt.debug_dir = os.path.join(opt.save_dir, 'debug')
        print('The output will be saved to ', opt.save_dir)

        if opt.resume and opt.load_model == '':
            model_path = opt.save_dir[:-4] if opt.save_dir.endswith('TEST') \
                else opt.save_dir
            opt.load_model = os.path.join(model_path, 'model_last.pth')
        if opt.task == 'objdet':
            opt.dataset = opt.task
        return opt

    def update_dataset_info_and_set_heads(self, opt, dataset):
        input_h, input_w = dataset.default_resolution
        opt.mean, opt.std = dataset.mean, dataset.std
        opt.num_classes = dataset.num_classes
        opt.class_names = dataset.class_names

        # input_h(w): opt.input_h overrides opt.input_res overrides dataset default
        input_h = opt.input_res if opt.input_res > 0 else input_h
        input_w = opt.input_res if opt.input_res > 0 else input_w
        opt.input_h = opt.input_h if opt.input_h > 0 else input_h
        opt.input_w = opt.input_w if opt.input_w > 0 else input_w
        opt.output_h = opt.input_h // opt.down_ratio
        opt.output_w = opt.input_w // opt.down_ratio
        opt.input_res = max(opt.input_h, opt.input_w)
        opt.output_res = max(opt.output_h, opt.output_w)

        if opt.task == 'exdet':
            # assert opt.dataset in ['coco']
            num_hm = 1 if opt.agnostic_ex else opt.num_classes
            opt.heads = {'hm_t': num_hm, 'hm_l': num_hm,
                         'hm_b': num_hm, 'hm_r': num_hm,
                         'hm_c': opt.num_classes}
            if opt.reg_offset:
                opt.heads.update(
                    {'reg_t': 2, 'reg_l': 2, 'reg_b': 2, 'reg_r': 2})
        elif opt.task == 'ddd':
            # assert opt.dataset in ['gta', 'kitti', 'viper']
            opt.heads = {'hm': opt.num_classes, 'dep': 1, 'rot': 8, 'dim': 3}
            if opt.reg_bbox:
                opt.heads.update(
                    {'wh': 2})
            if opt.reg_offset:
                opt.heads.update({'reg': 2})
        elif opt.task == 'ctdet':
            # assert opt.dataset in ['pascal', 'coco']
            opt.heads = {'hm': opt.num_classes,
                         'wh': 2 if not opt.cat_spec_wh else 2 * opt.num_classes}
            if opt.reg_offset:
                opt.heads.update({'reg': 2})
        elif opt.task == 'objdet':
            # assert opt.dataset in ['pascal', 'coco']
            opt.heads = {'hm': opt.num_classes,
                         'wh': 2 if not opt.cat_spec_wh else 2 * opt.num_classes}
            if opt.reg_offset:
                opt.heads.update({'reg': 2})

        elif opt.task == 'multi_pose':
            # assert opt.dataset in ['coco_hp']
            opt.flip_idx = dataset.flip_idx
            opt.heads = {'hm': opt.num_classes, 'wh': 2, 'hps': 34}
            if opt.reg_offset:
                opt.heads.update({'reg': 2})
            if opt.hm_hp:
                opt.heads.update({'hm_hp': 17})
            if opt.reg_hp_offset:
                opt.heads.update({'hp_offset': 2})
        else:
            assert 0, 'task not defined!'
        print('heads', opt.heads)
        return opt

    def init(self, args=''):

        default_dataset_info = {
            'ctdet': {'default_resolution': [512, 512], 'num_classes': 80,
                      'mean': [0.408, 0.447, 0.470], 'std': [0.289, 0.274, 0.278],
                      'dataset': 'coco'},
            'objdet': {'default_resolution': [512, 512], 'num_classes': None,
                       'mean': [0.408, 0.447, 0.470], 'std': [0.289, 0.274, 0.278],
                       'dataset': 'objdet'},
            'exdet': {'default_resolution': [512, 512], 'num_classes': 80,
                      'mean': [0.408, 0.447, 0.470], 'std': [0.289, 0.274, 0.278],
                      'dataset': 'coco'},
            'multi_pose': {
                'default_resolution': [512, 512], 'num_classes': 1,
                'mean': [0.408, 0.447, 0.470], 'std': [0.289, 0.274, 0.278],
                'dataset': 'coco_hp', 'num_joints': 17,
                'flip_idx': [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10],
                             [11, 12], [13, 14], [15, 16]]},
            'ddd': {'default_resolution': [384, 1280], 'num_classes': 3,
                    'mean': [0.485, 0.456, 0.406], 'std': [0.229, 0.224, 0.225],
                    'dataset': 'kitti'},
        }

        class Struct:
            def __init__(self, entries):
                for k, v in entries.items():
                    self.__setattr__(k, v)
        opt = self.parse(args)
        if opt.task == 'objdet':
            num_classes, class_names = read_classes.get_class_details()
            default_dataset_info[opt.task]['num_classes'] = num_classes
            default_dataset_info[opt.task]['class_names'] = class_names

        dataset = Struct(default_dataset_info[opt.task])
        opt.dataset = dataset.dataset
        opt = self.update_dataset_info_and_set_heads(opt, dataset)
        return opt
