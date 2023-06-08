import telebot
from telebot import types
from telebot.types import BotCommand
import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
import queue
import requests
from flask import request
from html2image import Html2Image
from PIL import Image
from flask import Flask, render_template
import threading
from queue import Queue
from threading import Lock
from collections import defaultdict