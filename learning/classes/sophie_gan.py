import torch
import torch.nn as nn
import torch.nn.functional as f 
import random
import numpy as np 

"""
    Straightforward LSTM encoder

    returns hidden state at last time step
    and process last layer of hidden state through a linear layer
    to get its size to input_size
    this is a returned and will be used as starting point for decoding
"""
class encoderLSTM(nn.Module):
    # def __init__(self,input_size,hidden_size,num_layers,output_size,batch_size,seq_len):
    
    def __init__(self,batch_size,input_size = 2,hidden_size = 32,num_layers = 1, embedding_size = 16):
        super(encoderLSTM,self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.embedding_size = embedding_size
        self.batch_size = batch_size

        self.embedding = nn.Linear(self.input_size,self.embedding_size)

        self.lstm = nn.LSTM(input_size = self.embedding_size,hidden_size = self.hidden_size,num_layers = self.num_layers,batch_first = True)
        

        

    def forward(self,x,x_lengths,nb_max):
        self.hidden = self.init_hidden_state(self.batch_size*nb_max)

        seq_len = x.size()[1]
        # print((self.batch_size*seq_len*nb_max,self.input_size))

        
        x = x.view(self.batch_size*seq_len*nb_max,self.input_size)
        x = self.embedding(x)
        x = x.view(self.batch_size * nb_max,seq_len,self.embedding_size)

        x = f.relu(x)

        x = torch.nn.utils.rnn.pack_padded_sequence(x, x_lengths, batch_first=True)
        x,self.hidden = self.lstm(x,self.hidden)
        x, _ = torch.nn.utils.rnn.pad_packed_sequence(x, batch_first=True)
        
        return x[:,-1,:]



    def init_hidden_state(self,batch_size):
        h_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()
        c_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()

        return (h_0,c_0)


class generatorLSTM(nn.Module):
    # def __init__(self,input_size,hidden_size,num_layers,output_size,batch_size,seq_len):
    
    def __init__(self,batch_size,input_size = 2,hidden_size = 32,num_layers = 1, embedding_size = 16):
        super(encoderLSTM,self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.embedding_size = embedding_size
        self.batch_size = batch_size

        self.embedding = nn.Linear(self.input_size,self.embedding_size)

        self.lstm = nn.LSTM(input_size = self.embedding_size,hidden_size = self.hidden_size,num_layers = self.num_layers,batch_first = True)
        

        

    def forward(self,x,x_lengths,nb_max):
        self.hidden = self.init_hidden_state(self.batch_size*nb_max)

        seq_len = x.size()[1]
        # print((self.batch_size*seq_len*nb_max,self.input_size))

        
        x = x.view(self.batch_size*seq_len*nb_max,self.input_size)
        x = self.embedding(x)
        x = x.view(self.batch_size * nb_max,seq_len,self.embedding_size)

        x = f.relu(x)

        x = torch.nn.utils.rnn.pack_padded_sequence(x, x_lengths, batch_first=True)
        x,self.hidden = self.lstm(x,self.hidden)
        x, _ = torch.nn.utils.rnn.pad_packed_sequence(x, batch_first=True)
        
        return x[:,-1,:]



    def init_hidden_state(self,batch_size):
        h_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()
        c_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()

        return (h_0,c_0)


class SoftAttention(nn.Module):
    # def __init__(self,input_size,hidden_size,num_layers,output_size,batch_size,seq_len):
    
    def __init__(self,batch_size,input_size,output_size,hdec_size ,nb_weights,layers = [64,128,64]):
        super(SoftAttention,self).__init__()

        self.hdec_size = hdec_size
        self.output_size = output_size
        self.input_size = input_size

        self.nb_weights = nb_weights
        self.batch_size = batch_size
        self.layers = [hdec_size] + layers + [nb_weights]
        self.features_embedding = nn.Linear(input_size,output_size)
        modules = []
        for i in range(1,len(self.layers)):
            modules.append(nn.Linear(self.layers[i-1],self.layers[i]))
            if i < len(self.layers) -1 :
                modules.append(nn.ReLU())
        self.core = nn.Sequential(*modules)
        


        

    def forward(self,hdec,features,zero_weigths = None,apply_weigths_filter = True):
        features = self.features_embedding(features)
        features = f.relu(features)
        # attn_weigths = f.softmax(self.core(hdec),dim = 1)
        attn_weigths = self.core(hdec)

        # set to zero the weight of padding(no vehicule present)
        if apply_weigths_filter :
            attn_weigths *= zero_weigths
        


        

        attn_applied = torch.bmm(attn_weigths, features)
        
        return attn_applied



    def init_hidden_state(self,batch_size):
        h_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()
        c_0 = torch.rand(self.num_layers,batch_size,self.hidden_size).cuda()

        return (h_0,c_0)

    
"""
    Straightforward LSTM decoder
    Uses prediction at timestep t-1 as input 
    to predict timestep t
"""
class decoderLSTM(nn.Module):
    # def __init__(self,input_size,hidden_size,num_layers,output_size,batch_size,seq_len):
    
    def __init__(self,batch_size,input_size,output_size,hidden_size,num_layers):
        super(decoderLSTM,self).__init__()

        self.batch_size = batch_size
        self.input_size = input_size

        self.output_size = output_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        
        self.lstm = nn.LSTM(input_size = input_size,hidden_size = hidden_size,num_layers = num_layers,batch_first = True)
        self.out = nn.Linear(self.hidden_size,self.output_size)

        

    def forward(self,x,hidden):
        # self.hidden = self.init_hidden_state()
        # x = x.view(self.seq_len,self.batch_size,2)
        output,self.hidden = self.lstm(x,hidden)
        output = self.out(output)#activation?
        return output, hidden

    def init_hidden_state(self):
        h_0 = torch.rand(self.num_layers,self.batch_size,self.hidden_size).cuda()
        c_0 = torch.rand(self.num_layers,self.batch_size,self.hidden_size).cuda()

        return (h_0,c_0)


class discriminatorLSTM(nn.Module):
    # def __init__(self,input_size,hidden_size,num_layers,output_size,batch_size,seq_len):
    
    def __init__(self,batch_size,input_size = 2,embedding_size = 16,hidden_size = 64,num_layers = 1,seq_len = 20):
        super(discriminatorLSTM,self).__init__()

        self.batch_size = batch_size
        self.input_size = input_size
        self.embedding_size = embedding_size


        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.seq_len = seq_len
        self.output_size = 1
        

        self.embedding = nn.Linear(input_size,embedding_size)
        self.lstm = nn.LSTM(input_size = embedding_size,hidden_size = hidden_size,num_layers = num_layers,batch_first = True)
        
        self.out = nn.Linear(self.hidden_size,self.output_size)

        

    def forward(self,x):
        self.hidden = self.init_hidden_state()

        x = x.view(-1,self.input_size)
        x = self.embedding(x)
        x = x.view(self.batch_size,self.seq_len,self.embedding_size)

        _,self.hidden = self.lstm(x,self.hidden)
        x = self.out(self.hidden[0])
        x = torch.sigmoid(x)
        return x

    def init_hidden_state(self):
        h_0 = torch.rand(self.num_layers,self.batch_size,self.hidden_size).cuda()
        c_0 = torch.rand(self.num_layers,self.batch_size,self.hidden_size).cuda()

        return (h_0,c_0)
"""
    
"""
class sophie(nn.Module):
    def __init__(self,
            batch_size,
            enc_input_size = 2,
            enc_hidden_size = 32,
            enc_num_layers = 1, 
            embedding_size = 16,
            dec_hidden_size = 32,
            nb_neighbors_max = 51,
            social_features_embedding_size = 16,
            gaussian_dim = 8,
            dec_num_layer = 1,
            output_size = 2,
            pred_length = 12,
            obs_length = 8,

            disc_hidden_size = 64,
            disc_nb_layer = 1

            ):
        super(sophie,self).__init__()
        self.encoder = encoderLSTM(batch_size,enc_input_size,enc_hidden_size,enc_num_layers,embedding_size)
        self.batch_size = batch_size
        self.enc_input_size = enc_input_size
        self.enc_hidden_size = enc_hidden_size
        self.enc_num_layers = enc_num_layers
        self.embedding_size = embedding_size
        self.dec_hidden_size = dec_hidden_size
        self.nb_neighbors_max = nb_neighbors_max
        self.pred_length = pred_length
        self.obs_length = obs_length

        self.output_size = output_size
        self.disc_hidden_size = disc_hidden_size
        self.disc_nb_layer = disc_nb_layer



        self.gaussian = torch.distributions.MultivariateNormal(torch.zeros(gaussian_dim),torch.eye(gaussian_dim))
        self.social_features_embedding_size = social_features_embedding_size
        self.social_attention = SoftAttention(batch_size,enc_hidden_size,social_features_embedding_size,dec_hidden_size ,nb_neighbors_max)
        
        dec_input_size = gaussian_dim + 1*embedding_size + 0*embedding_size
        
        self.generator = decoderLSTM(batch_size,dec_input_size,output_size,dec_hidden_size,dec_num_layer)
        self.discriminator = discriminatorLSTM(2*batch_size,enc_input_size,embedding_size,disc_hidden_size,disc_nb_layer,pred_length + obs_length)
        

    def forward(self,x,y):
        B,N,S,I = x.size()

        # number of active agent per batch
        agent_numbers = self.__get_number_agents(x)
        
        # reshape so that new batch size is former batch_size * nb_max agents
        output = x.view(B*N,S,I)

        # get lengths of sequences(without padding) in ascending order
        x_lengths = self.__get_lengths_x(output.cpu().detach().numpy(),S)
        x_lengths = np.array(x_lengths)

        
        
        

        # get the indices of the descending sorted lengths
        arg_ids = list(reversed(np.argsort(x_lengths)))

        # order input vector based on descending sequence lengths
        output = output[arg_ids]

        # get ordered/unpadded sequences lengths for pack_padded object
        sorted_x_lengths = x_lengths[arg_ids]

        # encode
        output = self.encoder(output,sorted_x_lengths,N)

        # reverse ordering of indices
        rev_arg_ids = np.argsort(arg_ids)
        # reverse ordering of encoded sequence
        output = output[rev_arg_ids]
        # reshape to original batch_size
        output = output.view(B,N,self.enc_hidden_size)

        
        # social features, sort hidden states by euclidean distance
        # remove main agent hidden state
        Vsos = self.__get_social_features(x_lengths,x,output)

       
        
        # nb of attention weigths to set to zero
        nb_padded_agents = -1*( np.array(agent_numbers) -(N+1))
        zero_weigths = np.ones((B,self.nb_neighbors_max))
        for i,n in enumerate(nb_padded_agents):
            zero_weigths[i][n:] = 0
        zero_weigths = torch.FloatTensor(zero_weigths).view(B,1,self.nb_neighbors_max).cuda()
        
        
        
        

        # C = torch.cat([Co,z], dim = 2)
        generator_outputs = self.__generate(Vsos,zero_weigths)

        observations = x[:,0].view(self.batch_size,self.obs_length,self.output_size)

        ground_truth = y[:,0].view(self.batch_size,self.pred_length,self.output_size)

        pred_traj = torch.cat([observations,generator_outputs], dim = 1)
        real_traj = torch.cat([observations,ground_truth], dim = 1)

        pred_labels = torch.zeros(self.batch_size)
        gt_labels = torch.ones(self.batch_size)


        labels = torch.cat([pred_labels,gt_labels],dim = 0).cuda()
        traj = torch.cat([pred_traj,real_traj],dim = 0)
        
        sort = np.arange(self.batch_size * 2)
        np.random.shuffle(sort) 

        labels = labels[sort]
        traj = traj[sort]

        disc_class = self.discriminator(traj).view(2*self.batch_size)
        
        gan_loss = nn.BCELoss()
        g_loss = gan_loss(disc_class,labels)

        mse = nn.MSELoss(reduction= "none")

        # sum over a trajectory, average over batch size
        mse_loss = torch.mean(torch.sum(torch.sum(mse(generator_outputs,ground_truth),dim = 2),dim = 1))



        print(mse_loss.item())



        

        return

    def __generate(self,Vsos,zero_weigths):
        state = self.generator.init_hidden_state()
        # geerate one random tensor per batch
        z = self.gaussian.sample((self.batch_size,1,)).cuda()

        print(state[0].size())
        # apply social attention to get a unique feature vector per sample
        Co = self.social_attention(state[0][0].view(self.batch_size,1,self.dec_hidden_size),Vsos,zero_weigths)
        C = torch.cat([Co,z], dim = 2)

        outputs = []

        for _ in range(self.pred_length):
            
            output,state = self.generator(C,state)
            outputs.append(output)

            Co = self.social_attention(state[0][0].view(self.batch_size,1,self.dec_hidden_size),Vsos,zero_weigths)
            C = torch.cat([Co,z], dim = 2)

        outputs = torch.stack(outputs).view(self.batch_size,self.pred_length,self.output_size)
        return outputs

    def __get_social_features(self,x_lengths,x,output):
        B,N,S,I = x.size()
        # get sequences last points
        last_points = torch.stack([s[i-1,:] for i,s in zip(x_lengths,x.view(B*N,S,I))])
        last_points = last_points.view(B,N,I)

        # get main agent last point
        reference_points = last_points[:,0].view(B,1,self.enc_input_size).repeat(1,N,1)
       
        # compute euclidean distance
        dist = torch.sqrt(torch.sum(torch.pow(last_points-reference_points,2),dim = 2)) # B*Nmax

        Vsos = []
        for hiddens,d in zip(output,dist):
            ids = np.argsort(d)
            hiddens = hiddens[ids]
            Vso = hiddens-hiddens[0].repeat(N,1)
            Vso = Vso[1:]
            Vsos.append(Vso)
        Vsos = torch.stack(Vsos).view(B,N-1,self.enc_hidden_size)

        return  Vsos


    def __get_lengths_x(self,x,seq_len,padding = -1):
        x_lengths = []
        for i,sequence in enumerate(x):
            unpadded_length = 0
            for point in sequence:
                if point[0] != padding:
                    unpadded_length += 1
            if unpadded_length == 0:
            #     empty_trajectories_ids.append(i)
                unpadded_length += 1

            x_lengths.append(unpadded_length)
        return x_lengths

    def __get_number_agents(self,x,padding = -1):
        agent_numbers = []
        for sample in x:
            nb_agent = 0
            for sequence in sample:
                # if sequence[-1][0] != padding:
                if sequence[0][0] != padding:                
                    nb_agent += 1
            agent_numbers.append(nb_agent)
        return agent_numbers





