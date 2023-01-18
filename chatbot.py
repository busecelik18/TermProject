# -*- coding: utf-8 -*-
"""chatbot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o4u9nKD-NaH5A2Kqv7cAPWVcOECB8e2l
"""

#Imports libraries like tensorflow, numpy, matplotlib, sklearn. Tensorflow is a library for artificial neural networks and deep learning. 
#Numpy is a library for mathematical calculations. Matplotlib is a library used to generate graphs. 
#Sklearn is a library for using machine learning algorithms.

import tensorflow as tf

import unicodedata
import re
import numpy as np
import os
import io
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.model_selection import train_test_split


import warnings
warnings.filterwarnings('ignore')

"""# Prepare Data

It reads a dataset named 'dialogs.txt' and reads its contents. Next, the contents of the dataset are compiled into a list and this list is divided into questions and answers. These lists are assigned to variables named 'questions' and 'answers'.

This snippet splits each line in the file by the '\n' character and splits each line by the '\t' character. Thus, the first part of each line is considered a question, and the second part is considered an answer. These questions and answers are assigned to the 'questions' and 'answers' lists.
"""

#The code reads the contents of a dataset named 'dialogs.txt' and compiles them into lists of questions and answers. It uses the '\n' and '\t' characters to separate 
#the lines and distinguish between questions and answers, which are then assigned to variables.
file = open('dialogs.txt','r').read()
qna_list = [f.split('\t') for f in file.split('\n')]

questions = [x[0] for x in qna_list]
answers = [x[1] for x in qna_list]

"""It is used to print data stored in the 'questions' and 'answers' lists. In particular, the data in the questions[2] and answers[2] indexes are being printed. This data represents the question and answer on line 3 in the dialog dataset."""

print("Q: ", questions[2])
print("A: ", answers[2])

"""# Preprocessing the sentences

It contains two functions that perform the preprocessing steps of a given sentence.

The "unicode_to_ascii(s)" function converts a given unicode sentence to ascii characters. This function converts each character in the sentence into NFD (Canonical Syntax Form) form with the unicodedata.normalize() function and then checks the category of the character using the unicodedata.category() function for each character of the sentence. If the character has Mn (Mark) in its category, that character is removed from the sentence.

The "preprocess_sentence(w)" function cleans up a given sentence and performs the preprocessing steps. First, the sentence is lowercase and leading and trailing spaces are deleted. Then a space is placed between the punctuation marks in the sentence. If there is more than one space in the sentence, it is made into a single space. Only letters, punctuation marks and numbers remain in the sentence. Finally, the sentence starts with <start> and ends with <end>.
"""

#The code has two functions for preprocessing sentences, converting unicode to ascii and cleaning up the sentence by lowercasing, removing extra spaces, 
#and keeping only letters, punctuation marks, numbers and adding a '.' at the start and end.
def unicode_to_ascii(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
      if unicodedata.category(c) != 'Mn')


def preprocess_sentence(w):
    w = unicode_to_ascii(w.lower().strip())

    w = re.sub(r"([?.!,¿])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)

    w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
    w = w.strip()

    w = '<start> ' + w + ' <end>'
    return w

"""It processes the sentences in the 'questions' and 'answers' lists using the preprocessing functions and saves the new lists as 'pre_questions' and 'pre_answers'. First, the sentences in the questions[0] and answers[0] indexes are inserted into the preprocessing functions and printed to the screen. Next, all the sentences in the questions and answers lists are inserted into the preprocessing functions and the new lists are saved as pre_questions and pre_answers. This step is the preprocessing necessary for the chatbot to understand the questions and answers later."""

#It processes the sentences in the `questions' and 'answers' lists using the preprocessing functions and saves the new lists as 'pre_questions' and 'pre_answers'.
#First, the sentences in the questions[0] and answers[0] indexes are inserted into the preprocessing functions and printed to the screen.
print(preprocess_sentence(questions[0]))
print(preprocess_sentence(answers[0]))

pre_questions = [preprocess_sentence(w) for w in questions]
pre_answers = [preprocess_sentence(w) for w in answers]

"""# Tokenizing

Creates a function to tokenize the given language. Tokenization is the process of converting texts into numeric values. These numerical values are processed by artificial neural networks.

Inside the function, a Tokenizer object is created. This object is used to clean the filters. Next, the tokenizer object is trained to the texts of the given language with the fit_on_texts() function.

Then the texts are converted to numeric values using the tokenizer object. These numeric values are saved in the tensor variable.

Finally, the tensor values are padded with zeros with the pad_sequences() function. This ensures that all sentences are the same length. The function returns the tensor and lang_tokenizer values.
"""

#Creates a function to tokenize the given language. Tokenization is the process of converting texts into numeric values.
#Next, the tokenizer object is trained to the texts of the given language with the fit_on_texts() function.
#Then the texts are converted to numeric values using the tokenizer object. The function returns the tensor and lang_tokenizer values.
def tokenize(lang):
    lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(
      filters='')
    lang_tokenizer.fit_on_texts(lang)

    tensor = lang_tokenizer.texts_to_sequences(lang)

    tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor,
                                                         padding='post')

    return tensor, lang_tokenizer

"""Creates a function to load the given dataset. This function creates cleaned input-output pairs using the 'pre_questions' and 'pre_answers' lists.
The function also ensures that the number of samples specified by the num_examples variable is taken.

Next, the function tokenizes the 'pre_questions' and 'pre_answers' lists using the tokenize() function. This tokenized data is saved in the input_tensor and target_tensor variables.

Finally, it returns the tokenizer objects along with the generated input_tensor and target_tensor values.
"""

#This function creates cleaned input-output pairs using the `pre_questions' and 'pre_answers' lists.
#Next, the function tokenizes the 'pre_questions' and 'pre_answers' lists using the tokenize() function.
#This tokenized data is saved in the input_tensor and target_tensor variables.
def load_dataset(data, num_examples=None):
    # creating the cleaned input, output pairs
    if(num_examples != None):
        targ_lang, inp_lang, = data[:num_examples]
    else:
        targ_lang, inp_lang, = data

    input_tensor, inp_lang_tokenizer = tokenize(inp_lang)
    target_tensor, targ_lang_tokenizer = tokenize(targ_lang)

    return input_tensor, target_tensor, inp_lang_tokenizer, targ_lang_tokenizer

"""It loads the dataset consisting of the 'pre_answers' and 'pre_questions' lists and takes the amount of samples specified by the num_examples variable. It is assigned to the variables 'input_tensor', 'target_tensor', 'inp_lang' and 'targ_lang' with the 'load_dataset' function.

Next, the maximum length of 'target_tensor' is calculated as 'max_length_targ' and the maximum length of 'input_tensor' is 'max_length_inp'. These values will be used to determine the lengths of the inputs and outputs of the model that will be used later.
"""

#It is assigned to the variables 'input_tensor', 'target_tensor', 'inp_lang' and 'targ_lang' with the 'load_dataset' function.
#These values will be used to determine the lengths of the inputs and outputs of the model that will be used later.
num_examples = 30000
data = pre_answers, pre_questions
input_tensor, target_tensor, inp_lang, targ_lang = load_dataset(data, num_examples)

# Calculate max_length of the target tensors
max_length_targ, max_length_inp = target_tensor.shape[1], input_tensor.shape[1]

"""It uses 'input_tensor' and 'target_tensor' to separate datasets into training and validation sets. The train_test_split() function splits the 'input_tensor' and 'target_tensor' datasets as 80% training 20% validation.

Finally, using the "len()" function, the lengths of the training and validation sets are printed to the screen.
"""

# Creating training and validation sets using an 80-20 split
input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(input_tensor, target_tensor, test_size=0.2)

# Show length
print(len(input_tensor_train), len(target_tensor_train), len(input_tensor_val), len(target_tensor_val))

"""# Word to index

It recycles using a given tensor (numerical dataset) and a language tokenizer. The function recycles each numeric value in the given tensor using the index_word property of the language tokenizer. The recycled word and numeric value are printed on the screen. This function can be used to convert the outputs of the model into real words and make it easier to understand what it says.
"""

#The function recycles each numeric value in the given tensor using the index_word property of the language tokenizer.
#The recycled word and numeric value are printed on the screen.
def convert(lang, tensor):
    for t in tensor:
        if t!=0:
            print ("%d ----> %s" % (t, lang.index_word[t]))

"""Using the "convert" function, it prints the numeric values of the first samples in the training sets converted to real words. First, the first instances of the training sets are determined as input_tensor_train[0] and target_tensor_train[0].
Then, using the convert function, the recycled version is printed on the screen. This process is done separately as "Input Language" and "Target Language". This process allows you to control what the outputs of the model represent and look like.
"""

#First, the first instances of the training sets are determined as input_tensor_train[0] and target_tensor_train[0].
#This process is done separately as "Input Language" and "Target Language".
print ("Input Language; index to word mapping")
convert(inp_lang, input_tensor_train[0])
print ()
print ("Target Language; index to word mapping")
convert(targ_lang, target_tensor_train[0])

"""# Creating the Tensorflow dataset

Prepares datasets in such a way that the model can be used for training. First, the "BUFFER_SIZE" variable, which will be used to randomly select samples from the datasets, is set as the length of the "input_tensor_train" dataset. In addition, the "BATCH_SIZE" variable to be used in each training step is determined.

Then, using the "tf.data.Dataset.from_tensor_slices()" function, datasets consisting of input and target tensors are created and random samples are selected with the "shuffle()" function. Then, with the "batch()" function, the datasets are grouped by BATCH_SIZE.

Finally, the first samples are taken from the dataset variable and its dimensions are printed on the screen using the shape property. This process is used to verify that datasets are prepared correctly and grouped by BATCH_SIZE.
"""

#First, the "BUFFER_SIZE" variable, which will be used to randomly select samples from the datasets, is set as the length of the "input_tensor_train" dataset.
#In addition, the "BATCH_SIZE" variable to be used in each training step is determined.
#This process is used to verify that datasets are prepared correctly and grouped by BATCH_SIZE.
BUFFER_SIZE = len(input_tensor_train)
BATCH_SIZE = 64
steps_per_epoch = len(input_tensor_train)//BATCH_SIZE
embedding_dim = 256
units = 1024
vocab_inp_size = len(inp_lang.word_index)+1
vocab_tar_size = len(targ_lang.word_index)+1

dataset = tf.data.Dataset.from_tensor_slices((input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)

example_input_batch, example_target_batch = next(iter(dataset))
example_input_batch.shape, example_target_batch.shape

"""# Encoder/Decoder classes with attention equations

## Encoder

Defining an encoder class. An encoder is a layer that converts a text input to numeric values and converts these numeric values into a format that the model can understand.

The encoder class takes parameters such as "vocab_size" (vocabulary size), "embedding_dim" (size of input vectors), "enc_units" (size of output vectors), and "batch_sz" (number of samples to use in each training step).

Inside the class, the Embedding layer is created. This layer works with the input texts converted to numeric values. Then the GRU layer is created. This layer creates a meaningful summary of the input texts and returns a vector as output.

The "call()" method makes the encoder layer work. Inside this method, input texts are converted to numeric values as a result of the embedding layer working. A meaningful summary of the texts is then created using the "gru" layer, and this summary is output as a vector. At the same time, the last state of the GRU layer is returned.

The "initialize_hidden_state()" method sets the initial state (initial state) of the GRU layer as a zero vector. This method is called before each training step and is used to set the initial state of the GRU layer as a zero vector.

This Encoder class is used to generate a meaningful summary of text inputs and convert that summary into a format that the model can understand. This digest is then used by the decoder layer.
"""

#This layer creates a meaningful summary of the input texts and returns a vector as output.
#A meaningful summary of the texts is then created using the "gru" layer, and this summary is output as a vector.
class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, enc_units, batch_sz):
        super(Encoder, self).__init__()
        self.batch_sz = batch_sz
        self.enc_units = enc_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(self.enc_units,
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')

    def call(self, x, hidden):
        x = self.embedding(x)
        output, state = self.gru(x, initial_state = hidden)
        return output, state

    def initialize_hidden_state(self):
        return tf.zeros((self.batch_sz, self.enc_units))

"""In this code cell, it creates a real encoder model using the predefined Encoder class. This model takes parameters such as "vocab_inp_size" (input vocabulary size), "embedding_dim" (size of input vectors), "units" (size of output vectors), and "BATCH_SIZE" (number of samples to use in each training step).

Next, the initial state of the encoder model is created using the "initialize_hidden_state()" method. This initial state is used before each training step and is used to set the start of operation of the encoder model as the zero vector.

Finally, the output and hidden state of the encoder model is generated using a sample input text named "example_input_batch". The dimensions of this output and the hidden state are printed, and if these dimensions are said to be correct, it means that the encoder model was created correctly.
"""

#This model takes parameters such as "vocab_inp_size" (input vocabulary size), "embedding_dim" (size of input vectors), "units" (size of output vectors),
# and "BATCH_SIZE" (number of samples to use in each training step).
encoder = Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)

# sample input
sample_hidden = encoder.initialize_hidden_state()
sample_output, sample_hidden = encoder(example_input_batch, sample_hidden)
print ('Encoder output shape: (batch size, sequence length, units) {}'.format(sample_output.shape))
print ('Encoder Hidden state shape: (batch size, units) {}'.format(sample_hidden.shape))

"""## Bahdanau Attention

In this code cell, it creates a class called "BahdanauAttention". This class is used to implement the Bahdanau Attention mechanism. The Attention mechanism is used to determine which parts of the vectors produced by the encoder layer should pay more attention to the decoder layer.

Bahdanau Attention is implemented using the "call()" method. This method takes two inputs named "query" (query vector) and "values" (value vectors). The "query" and "values" vectors are calculated by performing mathematical operations. Scores are returned as a tensor named "attention_weights". This tensor contains the score of each value vector, and these scores determine which parts the decoder layer should focus its attention on.

It also returns a tensor named "context_vector", which is the average of the vectors where the tensor query vector focuses on the value vectors.

The Bahdanau Attention mechanism enables the decoder layer to generate more meaningful responses.
"""

#This class is used to implement the Bahdanau Attention mechanism.
#This tensor contains the score of each value vector, and these scores determine which parts the decoder layer should focus its attention on.
class BahdanauAttention(tf.keras.layers.Layer):
    def __init__(self, units):
        super(BahdanauAttention, self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, query, values):
        # query hidden state shape == (batch_size, hidden size)
        # query_with_time_axis shape == (batch_size, 1, hidden size)
        # values shape == (batch_size, max_len, hidden size)
        # we are doing this to broadcast addition along the time axis to calculate the score
        query_with_time_axis = tf.expand_dims(query, 1)

        # score shape == (batch_size, max_length, 1)
        # we get 1 at the last axis because we are applying score to self.V
        # the shape of the tensor before applying self.V is (batch_size, max_length, units)
        score = self.V(tf.nn.tanh(
            self.W1(query_with_time_axis) + self.W2(values)))

        # attention_weights shape == (batch_size, max_length, 1)
        attention_weights = tf.nn.softmax(score, axis=1)

        # context_vector shape after sum == (batch_size, hidden_size)
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights

"""It creates a true attention model using the BahdanauAttention class defined in the previous snippet. This pattern is assigned to a variable named "attention_layer".

Next, the attention model is invoked using a sample latent state vector and a sample output vector. These sample entries are stored in variables named "sample_hidden" and "sample_output".

This call returns two tensors: "attention_result" and "attention_weights". The vector "attention_result" is the average of the vectors where the query vector focuses on the value vectors. The "attention_weights" tensor contains the score of each value vector.

If the attention_result and attention_weights shapes are correct, it means that the attention model is created correctly.
"""

#This pattern is assigned to a variable named "attention_layer". The "attention_weights" tensor contains the score of each value vector.
#If the attention_result and attention_weights shapes are correct, it means that the attention model is created correctly.
attention_layer = BahdanauAttention(10)
attention_result, attention_weights = attention_layer(sample_hidden, sample_output)

print("Attention result shape: (batch size, units) {}".format(attention_result.shape))
print("Attention weights shape: (batch_size, sequence_length, 1) {}".format(attention_weights.shape))

"""## Decoder class

Creates a true decoder model using the "Decoder" class defined in the previous snippet. This pattern is assigned to a variable named "decoder".

This model takes three inputs: x, hidden, and enc_output. x is the word index to be extracted by the decoder. hidden is the hidden state vector to be used by the decoder. enc_output are the output vectors produced by the encoder.

The decoder model uses an attention layer. This attention layer is defined in a variable named "attention". It generates the context vector and attention weights using the attention layer, hidden and enc_output inputs.

Then it reshapes x by adding x and context_vector. x is sent to the gru layer and the output vector is produced. The output vector is finally converted to word indexes via the fully connected layer.

This decoder pattern returns x and the state and attention_weights tensors as output.
"""

#This model takes three inputs: x, hidden, and enc_output. It generates the context vector and attention weights using the attention layer, hidden and enc_output inputs.
#This decoder pattern returns x and the state and attention_weights tensors as output.
class Decoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, dec_units, batch_sz):
        super(Decoder, self).__init__()
        self.batch_sz = batch_sz
        self.dec_units = dec_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(self.dec_units,
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')
        self.fc = tf.keras.layers.Dense(vocab_size)

        # used for attention
        self.attention = BahdanauAttention(self.dec_units)

    def call(self, x, hidden, enc_output):
        # enc_output shape == (batch_size, max_length, hidden_size)
        context_vector, attention_weights = self.attention(hidden, enc_output)

        # x shape after passing through embedding == (batch_size, 1, embedding_dim)
        x = self.embedding(x)

        # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)

        # passing the concatenated vector to the GRU
        output, state = self.gru(x)

        # output shape == (batch_size * 1, hidden_size)
        output = tf.reshape(output, (-1, output.shape[2]))

        # output shape == (batch_size, vocab)
        x = self.fc(output)

        return x, state, attention_weights

"""Produces a sample output for the decoder model created from the "Decoder" class defined in the previous snippet. The sample output is returned as the word index tensor that the decoder model produces as its output. This example output should have a shape of (batch_size, vocab size). If this snippet works fine, it means that the decoder pattern is correctly defined."""

#Produces a sample output for the decoder model created from the "Decoder" class defined in the previous snippet.
decoder = Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)

sample_decoder_output, _, _ = decoder(tf.random.uniform((BATCH_SIZE, 1)),
                                      sample_hidden, sample_output)

print ('Decoder output shape: (batch_size, vocab size) {}'.format(sample_decoder_output.shape))

"""This code defines the following:

optimizer: The optimizer used in the model, which is the Adam optimizer. The Adam optimizer is a commonly used optimization algorithm in deep learning, it's computationally efficient, has little memory requirement and invarient to diagonal rescale of the gradients.

loss_object: The loss function used to evaluate the model's performance. The loss function used is the SparseCategoricalCrossentropy loss, which is used for multi-class classification problem. The from_logits parameter is set to True, which indicates that the model's output is a logit. The reduction parameter is set to none, which means that the loss will not be averaged or summed across the batch dimension.

lossfunction: A custom loss function, which takes two arguments: real and pred. These represent the true labels and predicted labels respectively. The function applies a mask to the loss object to ignore any predictions made on padding (where real == 0) and then calculates the mean loss. The final loss is returned by the function. In the function, a logical not operation is applied to real values which are equal to zero and the result is casted to loss dtype.
"""

#The from_logits parameter is set to True, which indicates that the model's output is a logit.
#The reduction parameter is set to none, which means that the loss will not be averaged or summed across the batch dimension.
#The function applies a mask to the loss object to ignore any predictions made on padding (where real == 0) and then calculates the mean loss.
optimizer = tf.keras.optimizers.Adam()
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True, reduction='none')

def loss_function(real, pred):
    mask = tf.math.logical_not(tf.math.equal(real, 0))
    loss_ = loss_object(real, pred)

    mask = tf.cast(mask, dtype=loss_.dtype)
    loss_ *= mask

    return tf.reduce_mean(loss_)

"""This code defines a train_step function that is decorated with the @tf.function decorator. The function takes in three arguments: inp, targ, and enc_hidden.

inp: input data for the encoder
targ: target data for the decoder
enc_hidden: initial hidden state of the encoder
The function has the following steps:

Initialize the loss variable to 0
Start a GradientTape() context, which will record the operations for automatic differentiation
Pass the input and initial hidden state to the encoder to get the encoder output and the final hidden state
Set the initial hidden state of the decoder to be the final hidden state of the encoder
Set the initial input of the decoder to be the start token, repeated BATCH_SIZE times.
In a for loop, the decoder is passed the current input and hidden state, along with the encoder output. The predictions, final hidden state, and attention weights are returned by the decoder
The loss is calculated by passing the target and predictions to the loss_function and adding the resulting loss to the accumulated loss
The current input for the decoder is set to be the current target
After the loop, the average loss is calculated by dividing the accumulated loss by the number of time steps.
The variables to update are the trainable variables of both the encoder and decoder
The gradients are calculated by calling the tape.gradient method on the loss and variables
The optimizer is used to update the variables using the calculated gradients
The final batch loss is returned
The @tf.function decorator is used to convert the train_step function to a TensorFlow graph for performance optimization.
"""

#The predictions, final hidden state, and attention weights are returned by the decoder The loss is calculated by passing the target and predictions 
#to the loss_function and adding the resulting loss to the accumulated loss The current input for the decoder is set to be the current target
 #After the loop, the average loss is calculated by dividing the accumulated loss by the number of time steps.
@tf.function
def train_step(inp, targ, enc_hidden):
    loss = 0

    with tf.GradientTape() as tape:
        enc_output, enc_hidden = encoder(inp, enc_hidden)

        dec_hidden = enc_hidden

        dec_input = tf.expand_dims([targ_lang.word_index['<start>']] * BATCH_SIZE, 1)

        # Teacher forcing - feeding the target as the next input
        for t in range(1, targ.shape[1]):
            # passing enc_output to the decoder
            predictions, dec_hidden, _ = decoder(dec_input, dec_hidden, enc_output)

            loss += loss_function(targ[:, t], predictions)

            # using teacher forcing
            dec_input = tf.expand_dims(targ[:, t], 1)

    batch_loss = (loss / int(targ.shape[1]))

    variables = encoder.trainable_variables + decoder.trainable_variables

    gradients = tape.gradient(loss, variables)

    optimizer.apply_gradients(zip(gradients, variables))

    return batch_loss

"""In this cell, trains on the given dataset. It performs 40 epochs on the given data set. For each epoch, the hidden state on the encoder side is reset and the total loss is reset. Then the train_step function is called for each sample in the data set and the loss for each sample is added to the total loss variable. The average loss value is printed every 4th epoch."""

#It performs 40 epochs on the given data set.
EPOCHS = 40

for epoch in range(1, EPOCHS + 1):
    enc_hidden = encoder.initialize_hidden_state()
    total_loss = 0

    for (batch, (inp, targ)) in enumerate(dataset.take(steps_per_epoch)):
        batch_loss = train_step(inp, targ, enc_hidden)
        total_loss += batch_loss

    if(epoch % 4 == 0):
        print('Epoch:{:3d} Loss:{:.4f}'.format(epoch,
                                          total_loss / steps_per_epoch))

"""# Evaluating

This function is used to remove the "<start>" and "<end>" tags from a sentence. It takes a sentence as input and returns the sentence with the tags removed. The sentence is first split by "<start>" and then the last part of the split string is taken, which is the sentence without the "<start>" tag. This part is then again split by "<end>" and the first part of this split is taken, which is the sentence without the "<end>" tag. This is the final cleaned sentence that is returned.
"""

#The sentence is first split by "" and then the last part of the split string is taken, which is the sentence without the "" tag.
def remove_tags(sentence):
    return sentence.split("<start>")[-1].split("<end>")[0]

"""This code defines a function called evaluate that takes an input sentence and returns the translation of that sentence.

1)The input sentence is passed through a preprocess_sentence function to clean it up and make it suitable for the model.

2)The cleaned up sentence is then tokenized by splitting it into individual words and getting the corresponding index for each word in the input language's word index.

3)The tokenized sentence is then padded to a fixed maximum length (max_length_inp) using post-padding.

4)The padded input is converted to a TensorFlow tensor.

5)An empty string variable called result is initialized to store the generated translation.

6)The initial hidden state of the encoder is set to a zero tensor with shape (1, units), where units is the number of hidden units in the encoder.

7)The encoder is passed the input tensor and the initial hidden state to generate the encoder output and the final hidden state.

8)The decoder's initial hidden state is set to the final hidden state of the encoder, and the initial input is set to the start token.

9)In a for loop, the decoder is passed the current input and hidden state, along with the encoder output. The predictions, final hidden state, and attention weights are returned by the decoder.

10)The predicted word ID is obtained by taking the argmax of the predictions.

11)The predicted word is added to the result string.

12)If the predicted word is the end token, the function returns the result and the original sentence.

13)The predicted ID is then fed back into the model as the next input.

14)The loop continues until the maximum target length is reached or the end token is generated.

15)The final result is passed through a remove_tags function to remove any special tags.

In short, this function takes an input sentence and uses the encoder-decoder model to generate a translation for it, the function takes a sentence as input, preprocess it, tokenize it, pad it and convert it to a tensor then pass it to the encoder to get the hidden state and the encoder output, then it pass this output to the decoder along with the hidden state and the start token, it then iteratively predict the next word using the decoder until it reaches the end token or max_length_targ, then the function returns the final predicted sentence and the original sentence.
"""

#This function generates a translation of a sentence using the encoder-decoder model. It takes a sentence as input, preprocess it, tokenize it, 
#pad it and convert it to a tensor. It then passes this output to the decoder along with the hidden state and the start token or max_length_targ.
def evaluate(sentence):
    sentence = preprocess_sentence(sentence)

    inputs = [inp_lang.word_index[i] for i in sentence.split(' ')]
    inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs],
                                                         maxlen=max_length_inp,
                                                         padding='post')
    inputs = tf.convert_to_tensor(inputs)

    result = ''

    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)

    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([targ_lang.word_index['<start>']], 0)

    for t in range(max_length_targ):
        predictions, dec_hidden, attention_weights = decoder(dec_input,
                                                             dec_hidden,
                                                             enc_out)

        # storing the attention weights to plot later on
        attention_weights = tf.reshape(attention_weights, (-1, ))

        predicted_id = tf.argmax(predictions[0]).numpy()

        result += targ_lang.index_word[predicted_id] + ' '

        if targ_lang.index_word[predicted_id] == '<end>':
            return remove_tags(result), remove_tags(sentence)

        # the predicted ID is fed back into the model
        dec_input = tf.expand_dims([predicted_id], 0)

    return remove_tags(result), remove_tags(sentence)

"""# Answering the question"""

def ask(sentence):
    result, sentence = evaluate(sentence)

    print('Question: %s' % (sentence))
    print('Predicted answer: {}'.format(result))

ask(questions[4])

ask(questions[8])

"""#API

"""

while True:
    sentence = input("Ask a question:")
    result, sentence = evaluate(sentence)
    print('Predicted answer: {}'.format(result))