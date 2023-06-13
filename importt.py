import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
import queue
from queue import Queue
import threading
from threading import Lock
from collections import defaultdict
import telebot
from telebot import types
from telebot.types import BotCommand
from jinja2 import Template
import requests
from flask import Flask, render_template, request
from html2image import Html2Image
from PIL import Image